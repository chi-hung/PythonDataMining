#!/bin/bash
# This script disables the Nouveau driver

CL='\033[1;32m'   # default color
NC='\033[0m'      # no color

# disable Nouveau
echo -e "${CL}To install the NVIDIA Display Driver, the open-source driver 'Nouveau' has to be disabled. Now, let's disable Nouveau.${NC}"
echo 'blacklist nouveau
options nouveau modeset=0' > /etc/modprobe.d/blacklist-nouveau.conf
update-initramfs -u
if [ $? -eq 0 ];then
  echo -e "${CL}Nouveau is disabled. To take effect, We have to reboot the system. The system will reboot after 10 seconds.${NC}"
  sleep 10
  reboot
else
  echo -e "${CL}Something wrong while executing 'update-initramfs'!${NC}"
  exit 1
fi
