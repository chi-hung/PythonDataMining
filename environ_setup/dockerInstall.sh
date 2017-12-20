#!/bin/bash

# ------------------------------------------------
# This script installs Docker & NVIDIA-Docker.
# ------------------------------------------------

# Pre-install.
apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Get and install Docker.
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update && apt-get upgrade -y
apt-get install -y docker-ce

# Get and install Nvidia-Docker.
wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1-1_amd64.deb
dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb