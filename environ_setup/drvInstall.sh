#!/bin/bash
# ===============================================================================================
# This script installs NVIDIA Display Driver & CUDA ToolKit & cuDNN
#
# maintainer: Chi-Hung Weng (wengchihung@gmail.com)
# ===============================================================================================

# first, update the system to the latest state and get some basic tools
apt-get update && apt-get -y upgrade && apt-get install -y build-essential htop vim dkms ssh

# define names of the installer and where they can be retrieved
nvDrvInstaller='NVIDIA-Linux-x86_64-384.66.run'
nvDrvInstallerURL='http://us.download.nvidia.com/XFree86/Linux-x86_64/384.66/NVIDIA-Linux-x86_64-384.66.run'

cudaInstaller='cuda_8.0.61_375.26_linux.run'
cudaInstallerURL='https://developer.nvidia.com/compute/cuda/8.0/Prod2/local_installers/cuda_8.0.61_375.26_linux-run'

cudaPatchInstaller='cuda_8.0.61.2_linux.run'
cudaPatchInstallerURL='https://developer.nvidia.com/compute/cuda/8.0/Prod2/patches/2/cuda_8.0.61.2_linux-run'

cuDNNTar="cudnn-8.0-linux-x64-v6.0.tar"
cuDNNTarURL="http://honghu.wengscafe.de:35703/$cuDNNTar"

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
# get CUDA Toolkit installer
if [ ! -f $cudaInstaller ];then
  wget -O $cudaInstaller $cudaInstallerURL
else
  echo -e "${CL}INFO: CUDA Installer downloaded.${NC}"
fi
# install CUDA Toolkit
which /usr/local/cuda/bin/nvcc
if [ $? -ne 0 ];then
  bash $cudaInstaller --no-opengl-libs --toolkit --silent # the --no-opengl-libs flag is important if it's a multi-GPU environment.
fi
which /usr/local/cuda/bin/nvcc
if [ $? -ne 0 ];then
  echo "${CL}Error! nvcc -V does not work as expected. CUDA Toolkit may NOT be installed properly!${NC}"
  exit 1
else
  echo -e "${LBLUE}$(/usr/local/cuda/bin/nvcc -V)${NC}"
fi
# get CUDA Toolkit patch installer
if [ ! -f $cudaPatchInstaller ];then
  wget -O $cudaPatchInstaller $cudaPatchInstallerURL
else
  echo -e "${CL}INFO: CUDA Patch Installer downloaded.${NC}"
fi
# install CUDA Toolkit Patch
bash $cudaPatchInstaller -a --silent # install CUDA 8 patch

# export CUDA's PATH
cat /etc/bash.bashrc | grep -Fxq 'export PATH=/usr/local/cuda-8.0/bin:${PATH}'
if [ $? -ne 0 ];then
  { echo 'export PATH=/usr/local/cuda-8.0/bin:${PATH}'; cat /etc/bash.bashrc; } >/etc/bash.bashrc.new
  mv /etc/bash.bashrc{.new,}
else
  echo -e "${CL}INFO: CUDA's PATH was set in /etc/bash.bashrc${NC}"
fi
# export CUDA's LD_LIBRARY_PATH
cat /etc/bash.bashrc | grep -Fxq 'export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64:${LD_LIBRARY_PATH}'
if [ $? -ne 0 ];then
  { echo 'export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64:${LD_LIBRARY_PATH}'; cat /etc/bash.bashrc; } >/etc/bash.bashrc.new
  mv /etc/bash.bashrc{.new,}
else
  echo -e "${CL}INFO: CUDA's LD_LIBRARY_PATH was set in /etc/bash.bashrc${NC}"
fi

# get cuDNN library
if [ ! -f $cuDNNTar ];then
wget -O $cuDNNTar $cuDNNTarURL
else
  echo -e "${CL}INFO: cuDNN library downloaded.${NC}"
fi
# extract cuDNN library
tar -xvf $cuDNNTar -C /usr/local
