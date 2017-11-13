#!/bin/bash
# ===============================================================================================
# This script installs NVIDIA Display Driver & CUDA ToolKit & cuDNN
#
# maintainer: Chi-Hung Weng (wengchihung@gmail.com)
# ===============================================================================================

# first, update the system to the latest state and get some basic tools
apt-get update && apt-get -y upgrade && apt-get install -y build-essential htop vim dkms ssh

# define names of the installer and where they can be retrieved
nvDrvInstaller='NVIDIA-Linux-x86_64-384.81.run'
nvDrvInstallerURL='http://tw.download.nvidia.com/tesla/384.81/NVIDIA-Linux-x86_64-384.81.run'

# define colors which are used to display info messages
CL='\033[1;32m'   # default color
LBLUE="\033[1;34m"
NC='\033[0m'      # no color

# get the NVIDIA Display Driver installer
if [ ! -f $nvDrvInstaller ]; then
  wget -O $nvDrvInstaller $nvDrvInstallerURL
else
  echo -e "${CL}INFO: NVIDIA Display Driver Installer downloaded.${NC}"
fi

# install the NVIDIA Display Driver
which nvidia-smi
if [ $? -ne 0 ];then
  bash $nvDrvInstaller -a --silent --no-opengl-files --dkms
fi

# check if nvidia-smi works properly.
echo -e "${LBLUE}$(nvidia-smi)${NC}"
if [ $? -ne 0 ];then
  echo "${CL}Error! nvidia-smi does not work as expected. The NVIDIA Display Driver may NOT be installed properly!${NC}"
  exit 1
else
  echo -e "${CL}INFO: nvidia-smi works properly.${NC}"
fi