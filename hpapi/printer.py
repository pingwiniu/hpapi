import asyncio
import httpx
import xml.etree.ElementTree as ET

class Discover:
    def __init__(self):
        self.xml_namespace = "{http://www.hp.com/schemas/imaging/con/dictionaries/1.0/}"

    async def discover_printers(self):
        arp_result = await asyncio.create_subprocess_shell('arp -a', stdout=asyncio.subprocess.PIPE)
        arp_output = await arp_result.stdout.read()
        ip_list = [parts[0] for line in arp_output.decode().splitlines() if (parts := line.split()) and len(parts) >= 2 and '.' in parts[0]]

        printer_info_list = []

        async with httpx.AsyncClient() as client:
            for ip in ip_list:
                url = f"http://{ip}/DevMgmt/ProductConfigDyn.xml"
                try:
                    response = await client.get(url)
                    response.raise_for_status()

                    root = ET.fromstring(response.text)
                    version = root.find(f".//{self.xml_namespace}Version/{self.xml_namespace}Revision").text
                    make_model = root.find(f".//{self.xml_namespace}MakeAndModel").text
                    serial_number = root.find(f".//{self.xml_namespace}SerialNumber").text

                    printer_info_list.append({
                        'ip': ip,
                        'version': version,
                        'model': make_model,
                        'serial_number': serial_number
                    })

                except httpx.HTTPError as http_err:
                    pass
                except ET.ParseError as parse_err:
                    print(f"Error parsing XML for printer at {ip}: {parse_err}")

        printers_dict = {info['ip']: info for info in printer_info_list}
        return printers_dict


class Connect:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.xml_namespace = "{http://www.hp.com/schemas/imaging/con/dictionaries/1.0/}"

    async def scan_status(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f'http://{self.ip_address}/eSCL/ScannerStatus')

        if response.status_code == 200:
            xml_data = response.text
            root = ET.fromstring(xml_data)
            version = root.find(".//{http://www.pwg.org/schemas/2010/12/sm}Version").text
            state = root.find(".//{http://www.pwg.org/schemas/2010/12/sm}State").text

            jobs = []
            for job_info in root.findall(".//{http://schemas.hp.com/imaging/escl/2011/05/03}JobInfo"):
                job_uri = job_info.find(".//{http://www.pwg.org/schemas/2010/12/sm}JobUri").text
                job_uuid = job_info.find(".//{http://www.pwg.org/schemas/2010/12/sm}JobUuid").text
                age = job_info.find(".//{http://schemas.hp.com/imaging/escl/2011/05/03}Age").text
                images_completed = job_info.find(".//{http://www.pwg.org/schemas/2010/12/sm}ImagesCompleted").text
                images_to_transfer = job_info.find(".//{http://www.pwg.org/schemas/2010/12/sm}ImagesToTransfer").text
                job_state = job_info.find(".//{http://www.pwg.org/schemas/2010/12/sm}JobState").text
                job_state_reason = job_info.find(".//{http://www.pwg.org/schemas/2010/12/sm}JobStateReasons/{http://www.pwg.org/schemas/2010/12/sm}JobStateReason").text

                job_dict = {
                    "uuid": job_uuid,
                    "age": age,
                    "images_completed": images_completed,
                    "state": job_state,
                }
                jobs.append(job_dict)

            scanner_status = {
                "version": version,
                "state": state,
                "jobs": jobs
            }
            return scanner_status
        else:
            raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

    async def scan(self, file_type="pdf", color_mode="RGB24", resolution=300):

        if file_type.lower() not in ["pdf", "jpeg"]:
            raise ValueError("Invalid file type. Supported types are 'pdf' and 'jpeg'.")

        if color_mode not in ["RGB24", "Grayscale8"]:
            raise ValueError("Invalid color mode. Supported modes are 'RGB24' and 'Grayscale8'.")
        
        if resolution not in [75, 200, 300, 600]:
            raise ValueError("Invalid resolution. Supported values are 75, 200, 300, and 600.")

        url = f"http://{self.ip_address}/eSCL/ScanJobs"
        intent = "Document" if file_type.lower() == "pdf" else "Photo"

        xml_data = f"""<scan:ScanSettings xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03" xmlns:copy="http://www.hp.com/schemas/imaging/con/copy/2008/07/07" xmlns:dd="http://www.hp.com/schemas/imaging/con/dictionaries/1.0/" xmlns:dd3="http://www.hp.com/schemas/imaging/con/dictionaries/2009/04/06" xmlns:fw="http://www.hp.com/schemas/imaging/con/firewall/2011/01/05" xmlns:scc="http://schemas.hp.com/imaging/escl/2011/05/03" xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm">
            <pwg:Version>2.1</pwg:Version>
            <scan:Intent>{intent}</scan:Intent>
            <pwg:ScanRegions>
                <pwg:ScanRegion>
                    <pwg:Height>3507</pwg:Height>
                    <pwg:Width>2481</pwg:Width>
                    <pwg:XOffset>0</pwg:XOffset>
                    <pwg:YOffset>0</pwg:YOffset>
                </pwg:ScanRegion>
            </pwg:ScanRegions>
            <pwg:InputSource>Platen</pwg:InputSource>
            <scan:DocumentFormatExt>{'application/pdf' if file_type.lower() == "pdf" else 'image/jpeg'}</scan:DocumentFormatExt>
            <scan:XResolution>{resolution}</scan:XResolution>
            <scan:YResolution>{resolution}</scan:YResolution>
            <scan:ColorMode>{color_mode}</scan:ColorMode>
            <scan:CompressionFactor>45</scan:CompressionFactor>
            <scan:Brightness>800</scan:Brightness>
            <scan:Contrast>800</scan:Contrast>
        </scan:ScanSettings>
        """

        headers = {"Content-Type": "application/xml"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=xml_data, headers=headers)
                response.raise_for_status()
                location_header = response.headers.get('Location')

                if location_header:
                    location_with_next_document = f"{location_header}/NextDocument"
                    download_response = await client.get(location_with_next_document)
                    download_response.raise_for_status()

                    return download_response.content
                else:
                    raise Exception('The location header is not present (API mismatch?)')
            
            except httpx.HTTPError as http_err:
                print(f"Request failed with status code: {http_err.response.status_code}")
                print(http_err.response.text)
            except Exception as e:
                print(f"Error during scan: {e}")

        return None
    
    async def consumable_status(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f'http://{self.ip_address}/DevMgmt/ConsumableConfigDyn.xml')
                response.raise_for_status()
                root = ET.fromstring(response.content)
                consumable_info = {}
                for consumable_elem in root.iter('{http://www.hp.com/schemas/imaging/con/ledm/consumableconfigdyn/2007/11/19}ConsumableInfo'):
                    label_code = consumable_elem.find('{http://www.hp.com/schemas/imaging/con/dictionaries/1.0/}ConsumableLabelCode').text
                    percentage = consumable_elem.find('{http://www.hp.com/schemas/imaging/con/dictionaries/1.0/}ConsumablePercentageLevelRemaining').text
                    manufacturer = consumable_elem.find('{http://www.hp.com/schemas/imaging/con/dictionaries/1.0/}Manufacturer/{http://www.hp.com/schemas/imaging/con/dictionaries/1.0/}Name').text

                    consumable_info[label_code] = {
                        'percentage': percentage,
                        'manufacturer': manufacturer,
                    }

                return consumable_info

            except httpx.RequestError as e:
                return f"Error fetching data: {e}"
