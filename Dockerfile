# Use CUDA 12.2.2 base image
FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04

# Accept build-time arguments
ARG TASK_NAME
ARG BENCHMARK
ARG PROVIDER

ENV DEBIAN_FRONTEND=noninteractive \
    TASK_NAME=$TASK_NAME \
    BENCHMARK=$BENCHMARK \
    PROVIDER=$PROVIDER \
    NVIDIA_VISIBLE_DEVICES=all

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

# Install common dependencies from PyPI
RUN pip3 install tqdm click tabulate evaluate datasets transformers bitsandbytes onnx onnxruntime-gpu urllib3 rouge_score protobuf accelerate rich optimum

RUN pip3 install -i https://test.pypi.org/simple/ --no-deps agent-eval==0.1.13

RUN pip3 install -r requirements.txt 
RUN pip3 install -U "huggingface_hub[cli]"

RUN pip3 install -i https://test.pypi.org/simple/ agent-tasks

RUN git clone https://github.com/EleutherAI/lm-evaluation-harness && \
    cd lm-evaluation-harness && \
    pip install . && \
    cd .. && \
    rm -rf lm-evaluation-harness

# Set environment variables from build args
ENV TASK_NAME=$TASK_NAME
ENV BENCHMARK=$BENCHMARK
ENV PROVIDER=$PROVIDER

# Modify the CMD to include the Huggingface login
CMD ["sh", "-c", "huggingface-cli login --token $HUGGINGFACE_TOKEN && python3 run.py --task_name ${TASK_NAME} --benchmark ${BENCHMARK} --provider ${PROVIDER}"]
