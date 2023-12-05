from setuptools import setup, find_packages

setup(
    name='hpapi',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        'asyncio',
        'httpx',
    ],
    description='hpapi is a Python package for discovering and interacting with HP printers on the network. It allows users to discover printers, check their scanning status, and initiate scans. Please note that this package is not affiliated with HP and is an independent project.',
)
