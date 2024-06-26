# hpapi
hpapi is a Python package for discovering and interacting with HP printers on the network. It allows users to discover printers, check their scanning status, and initiate scans. Please note that this package is not affiliated with HP and is an independent project.

# WARNING!
This may not work on many hp models with different wsg servers, only some inkjet models work. This is basically reverse engineered api of the printing&scanning via the wsg server so it depends on it being the same, THE ONLY PRINTER 100% confirmed to be working is the DeskJet 5075

[![Downloads](https://static.pepy.tech/badge/hpapi)](https://pepy.tech/project/hpapi)
[![Downloads](https://static.pepy.tech/badge/hpapi/month)](https://pepy.tech/project/hpapi)

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Discover Class](#discover-class)
- [Connect Class](#connect-class)
- [Important Notes](#important-notes)
- [License](#license)
- [Creator](#creator)

## Installation

```bash
pip install hpapi
```

## Usage

```python
from hpapi import Discover, Connect

# Example usage
discovery = Discover()
printers = await discovery.discover_printers()
print(printers)

# Assuming 'printer_ip' is the IP address of an HP printer
connection = Connect(printer_ip)
status = await connection.scan_status()
print(status)

# Initiate a scan (example with default settings)
scan_result = await connection.scan()
if scan_result:
    with open('scanned_document.pdf', 'wb') as f:
        f.write(scan_result)
```

## Discover Class

### Methods

#### `discover_printers() -> dict`
Discovers HP printers on the local network and returns a dictionary with printer information.

## Connect Class

### Methods

#### `scan_status() -> dict`
Fetches the scanning status of the connected HP printer and returns a dictionary.

#### `scan(file_type: str = "pdf", color_mode: str = "RGB24", resolution: int = 300) -> bytes or None`
Initiates a scan with the specified settings and returns the scanned document content as bytes. Returns `None` on failure.

#### `consumable_status() -> dict or str`
Fetches the consumable status of the connected HP printer asynchronously and returns a dictionary containing information about consumables such as toner levels. Returns an error message as a string on failure.

## Important Notes

- **Disclaimer:** This project is not affiliated with HP.
- **Webscan and Authentication:** Webscan must be enabled, and authentication must be disabled for the package to work properly with HP printers.
- **Compatibility:** This package was tested with the HP DeskJet 5075 model.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
