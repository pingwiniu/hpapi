# Printer Utility Package

A Python package for discovering printers on the network and interacting with them for scanning purposes.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Discover Class](#discover-class)
- [Connect Class](#connect-class)
- [License](#license)
- [Creator](#creator)

## Installation

```bash
pip install printer-utility
```

## Usage

```python
from printer_utility import Discover, Connect

# Example usage
discovery = Discover()
printers = await discovery.discover_printers()
print(printers)

# Assuming 'printer_ip' is the IP address of a discovered printer
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
Discovers printers on the local network and returns a dictionary with printer information.

## Connect Class

### Methods

#### `scan_status() -> dict`
Fetches the scanning status of the connected printer and returns a dictionary.

#### `scan(file_type: str = "pdf", color_mode: str = "RGB24", resolution: int = 300) -> bytes or None`
Initiates a scan with the specified settings and returns the scanned document content as bytes. Returns `None` on failure.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Creator

- **Julian Zientkowski**
