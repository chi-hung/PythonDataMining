#!/bin/bash
# ===============================================================================================
# This script installs NVIDIA Driver & CUDA ToolKit & cuDNN
#
# NVIDIA DRIVER 384.98, CUDA9 and CUDNN7 shall be installed after executing this script.
#
# maintainer: Chi-Hung Weng (wengchihung@gmail.com)
# ===============================================================================================

# first, update the system to the latest state and get some basic tools
apt-get update && apt-get -y upgrade && apt-get install -y build-essential htop vim dkms ssh

# define names of the installer and where they can be retrieved
nvDrvInstaller='NVIDIA-Linux-x86_64-384.98.run'
#nvDrvInstallerURL='http://tw.download.nvidia.com/tesla/384.81/NVIDIA-Linux-x86_64-384.81.run'
nvDrvInstallerURL='http://us.download.nvidia.com/XFree86/Linux-x86_64/384.98/NVIDIA-Linux-x86_64-384.98.run'

#cudaInstaller='cuda_8.0.61_375.26_linux.run'
#cudaInstallerURL='https://developer.nvidia.com/compute/cuda/8.0/Prod2/local_installers/cuda_8.0.61_375.26_linux-run'
cudaInstaller='cuda_9.1.85_387.26_linux.run'
cudaInstallerURL='https://developer.nvidia.com/compute/cuda/9.1/Prod/local_installers/cuda_9.1.85_387.26_linux'

cudaPatchInstaller='cuda_8.0.61.2_linux.run'
cudaPatchInstallerURL='https://developer.nvidia.com/compute/cuda/8.0/Prod2/patches/2/cuda_8.0.61.2_linux-run'

#cuDNNTar="cudnn-8.0-linux-x64-v6.0.tar"
cuDNNTar="cudnn-9.0-linux-x64-v7.tgz"
cuDNNTarURL="http://honghu.wengscafe.de:35703/$cuDNNTar"

# define colors which are used to display info messages
CL='\033[1;32m'   # default color
LBLUE="\033[1;34m"
NC='\033[0m'      # no color

# get the NVIDIA Driver installer
if [ ! -f $nvDrvInstaller ]; then
  wget -O $nvDrvInstaller $nvDrvInstallerURL
else
  echo -e "${CL}INFO: NVIDIA Driver Installer was downloaded.${NC}"
fi

# install the NVIDIA Driver
echo -e "${CL}INFO: Checking if NVIDIA Driver was installed...${NC}"
cat /proc/driver/nvidia/version
if [ $? -ne 0 ];then
  echo -e "${CL}INFO: NVIDIA Driver was not installed...installing it Now...${NC}"
  bash $nvDrvInstaller -a --silent --no-opengl-files --dkms
  echo -e "${LBLUE}$(nvidia-smi)${NC}"
  echo -e "nvidia-smi | grep 'Driver Version' "
  if [ $? -ne 0 ];then
      echo "${CL}Error! nvidia-smi does not work as expected. The NVIDIA Driver may NOT be installed properly!${NC}"
      exit 1
  fi
else
  echo -e "${CL}INFO: NVIDIA Driver was installed!${NC}"
  #exit 1
fi

# get CUDA Toolkit installer
if [ ! -f $cudaInstaller ];then
  wget -O $cudaInstaller $cudaInstallerURL
else
  echo -e "${CL}INFO: CUDA Toolkit Installer was downloaded.${NC}"
fi
# install CUDA Toolkit
which /usr/local/cuda/bin/nvcc
if [ $? -ne 0 ];then
  echo -e "${CL}INFO: Installing CUDA Toolkit...${NC}"
  bash $cudaInstaller --no-opengl-libs --toolkit --silent # the --no-opengl-libs flag is important if it's a multi-GPU environment.
  # verify if CUDA Toolkit is installed
  which /usr/local/cuda/bin/nvcc
  if [ $? -ne 0 ];then
    echo "${CL}Error! nvcc -V does not work as expected. CUDA Toolkit may NOT be installed properly!${NC}"
    exit 1
  else
    echo -e "${LBLUE}$(/usr/local/cuda/bin/nvcc -V)${NC}"
    echo -e "${CL}INFO: CUDA Toolkit is now installed.${NC}"
  fi
else
  echo -e "${CL}INFO: CUDA Toolkit was installed!${NC}"
  #exit 1
fi

## get CUDA Toolkit patch installer
#if [ ! -f $cudaPatchInstaller ];then
#  wget -O $cudaPatchInstaller $cudaPatchInstallerURL
#else
#  echo -e "${CL}INFO: CUDA Toolkit Patch Installer was downloaded.${NC}"
#fi
## install CUDA Toolkit Patch
#echo -e "${CL}INFO: Installing CUDA Toolkit patch...${NC}"
#bash $cudaPatchInstaller -a --silent # install CUDA 8 patch

# export CUDA's PATH
cat /etc/bash.bashrc | grep 'export PATH=/usr/local/cuda-8.0/bin:${PATH}'
if [ $? -ne 0 ];then
  { echo 'export PATH=/usr/local/cuda-8.0/bin:${PATH}'; cat /etc/bash.bashrc; } >/etc/bash.bashrc.new
  mv /etc/bash.bashrc{.new,}
else
  echo -e "${CL}INFO: CUDA's PATH was set in /etc/bash.bashrc${NC}"
fi
# export CUDA's LD_LIBRARY_PATH
cat /etc/bash.bashrc | grep 'export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64:${LD_LIBRARY_PATH}'
if [ $? -ne 0 ];then
  { echo 'export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64:${LD_LIBRARY_PATH}'; cat /etc/bash.bashrc; } >/etc/bash.bashrc.new
  mv /etc/bash.bashrc{.new,}
else
  echo -e "${CL}INFO: CUDA's LD_LIBRARY_PATH was set in /etc/bash.bashrc${NC}"
fi

# get cuDNN
if [ ! -f $cuDNNTar ];then
wget -O $cuDNNTar $cuDNNTarURL
else
  echo -e "${CL}INFO: cuDNN library downloaded.${NC}"
fi
find /usr/local/cuda/lib64/ -name libcudnn* | grep -q "."
if [ $? -ne 0 ];then
  # extract cuDNN
  echo -e "${CL}INFO: Installing cuDNN...${NC}"
  tar -xvf $cuDNNTar -C /usr/local
  # verify if cuDNN is installed
  find /usr/local/cuda/lib64/ -name libcudnn* | grep -q "."
  if [ $? -ne 0 ];then
    echo -e "${CL}INFO: Error! Check if cudNN is installed properly.${NC}"
  else
    echo -e "${CL}INFO: cuDNN is now installed.${NC}"
  fi
else
  echo -e "${CL}INFO: cuDNN was installed. This script stops here and will not continue!${NC}"
  exit 1
fi
