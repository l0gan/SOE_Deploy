# SOE Setup Script

This script will setup a fresh testing VM for each engagement.

## Use:
`python3 SOE_setup.py`
Follow prompts... it's pretty easy.

## Setup:
- Install and setup WSL (if on Windows)
- Install Ansible (Inside WSL if on Windows)
- Install OVFTool from here: https://my.vmware.com/web/vmware/details?productId=352&downloadGroup=OVFTOOL350
- Install VMWare Fusion (Mac) or Workstation (Linux or Windows)
- Install Python3 (If running on Windows, Python3 can be installed in WSL or on host, depending on where you want to run from)
- Modify config.txt to ensure variables are correct
  - basePath: should be set to the c:/ path on Windows. Ensure all slashes are forward slashes (/). the script will flip as required if running in WSL.
  - OVATemplate: name of OVA template file (should reside in root of basePath)
  - privKeyLoc: location of ssh private key. if using Windows, this is the WSL accessible path (/mnt/c/...)
  - SOEuser: SOE Username (on Linux VM)
  - WSLBash: set to true if running SOE_Deploy inside WSL. If running SOE_Deploy on Windows host, Lunux, or Mac, set to false
- Run python3 SOE_setup.py
  - Enter customer name
  - Enter sudo password
  - Enter SSH Key password
