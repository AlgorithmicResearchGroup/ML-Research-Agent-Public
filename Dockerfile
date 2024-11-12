# Use CUDA 12.2.2 base image for GPU, or a generic Ubuntu image for CPU
ARG BASE_IMAGE=nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04
FROM ${BASE_IMAGE}

# Accept build-time arguments
ARG PROMPT
ARG PROVIDER

ENV DEBIAN_FRONTEND=noninteractive \
    PROMPT=$PROMPT \
    PROVIDER=$PROVIDER

# Install system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    git \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-distutils python3.11-dev \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --set python3 /usr/bin/python3.11 \
    && wget https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py \
    && rm get-pip.py \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the Python script and requirements to the working directory
COPY . /app

# Upgrade pip and install wheel
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

RUN pip3 install -r requirements.txt 
RUN pip3 install -U "huggingface_hub[cli]"

# Set environment variables from build args
ENV PROMPT=$PROMPT
ENV PROVIDER=$PROVIDER

# Modify the CMD to include the Huggingface login
ENTRYPOINT ["python3", "run.py"]