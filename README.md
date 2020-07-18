# Scanner

This is a utility script I wrote to help with using my flatbed scanner.

# Installation

This is currently being developed and has not been packaged appropriately

    poetry install .
    
    
## Arch Linux

    pacman -S tesseract xsane
    
# Configuration

This script requires the xsane command `scanimage`.  You can identify which devices are available by using the scanimage utility

    scanimage -L
    
    
There are two ways to define the XSANE options.

    export SCANNER_SANE_DEVICE=genesys:libusb:001:008
    export SCANNER_SANE_RESOLUTION=300
    
    
Once those are set, you can run the scanner script.

# Usage

When you run the script, it will ask how many pages you plan to 


# How does it work?
