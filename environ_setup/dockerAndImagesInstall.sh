#!/bin/bash

# -------------------------------------------------------------------------
# This script installs Docker & NVIDIA-Docker and pulls some docker images.
# -------------------------------------------------------------------------

# Pre-install.
apt-get install -y apt-transport-https ca-certificates curl software-properties-common

# Get and install Docker.
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get update && apt-get upgrade -y
apt-get install -y docker-ce

# Get and install NVIDIA-Docker.

# wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1-1_amd64.deb
# dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb

# ================================
# This section follows: https://github.com/NVIDIA/nvidia-docker
# If you have nvidia-docker 1.0 installed: we need to remove it and all existing GPU containers
docker volume ls -q -f driver=nvidia-docker | xargs -r -I{} -n1 docker ps -q -a -f volume={} | xargs -r docker rm -f
sudo apt-get purge -y nvidia-docker

# Add the package repositories
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu16.04/amd64/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update

# Install nvidia-docker2 and reload the Docker daemon configuration
sudo apt-get install -y nvidia-docker2
sudo pkill -SIGHUP dockerd
# ================================

# Test nvidia-smi with the latest official CUDA image

# Test if nvidia-smi works from a docker container.
nvidia-docker run --rm nvidia/cuda nvidia-smi

# obtain some popular images
docker pull nvidia/cuda
docker pull nvidia/caffe
docker pull nvidia/digits
docker pull pytorch/pytorch
docker pull caffe2ai/caffe2
#docker pull microsoft/cntk
##docker pull tensorflow/tensorflow:latest-gpu-py3

# Obtain Keras images built and maintained by me.
# Further info: https://github.com/chi-hung/DockerbuildsKeras
docker pull honghu/keras:tf-cu9-dnn7-py3-avx2-18.03
docker pull honghu/keras:cntk-cu9-dnn7-py3-18.03
docker pull honghu/keras:mx-cu9-dnn7-py3-18.03
docker pull honghu/keras:theano-cu9-dnn7-py3-18.03