#!/bin/bash

# Function to pull the Docker image if it's not already on the machine
pull_image() {
    local IMAGE_NAME=$1
    if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
        echo "Image $IMAGE_NAME not found locally. Pulling from Docker Hub..."
        docker pull "$IMAGE_NAME"
    else
        echo "Image $IMAGE_NAME already exists locally."
    fi
}

# Function to run the Docker container
run_container() {
    if [ "$#" -ne 6 ]; then
        echo "Usage: run_container <image_name> <prompt> <provider> <gpu_ids> <huggingface_token> <env_file_path>"
        echo "Example: run_container algorithmicresearch/agent:latest 'write an article on the history of python' openai 0 hf_token /home/ubuntu/.env"
        return 1
    fi

    local IMAGE_NAME="$1"
    local PROMPT="$2"
    local PROVIDER="$3"
    local GPU_IDS="$4"
    local HUGGINGFACE_TOKEN="$5"
    local ENV_FILE_PATH="$6"

    echo "IMAGE_NAME: $IMAGE_NAME"
    echo "PROMPT: $PROMPT"
    echo "PROVIDER: $PROVIDER"
    echo "GPU_IDS: $GPU_IDS"
    echo "HUGGINGFACE_TOKEN: $HUGGINGFACE_TOKEN"
    echo "ENV_FILE_PATH: $ENV_FILE_PATH"

    local CONTAINER_NAME="agent_${PROVIDER}_$(date +%Y%m%d_%H%M%S)"
    local HOST_OUTPUT_DIR="/home/ubuntu/agent_output/${CONTAINER_NAME}"

    # Ensure the host output directory exists
    mkdir -p "$HOST_OUTPUT_DIR"

    docker run -it \
        --name "$CONTAINER_NAME" \
        --gpus "device=$GPU_IDS" \
        -e NVIDIA_VISIBLE_DEVICES="$GPU_IDS" \
        -e HUGGINGFACE_TOKEN="$HUGGINGFACE_TOKEN" \
        -v "$HOST_OUTPUT_DIR:/app/output" \
        --env-file "$ENV_FILE_PATH" \
        -v "$ENV_FILE_PATH:/app/.env" \
        "$IMAGE_NAME" \
        --prompt "$PROMPT" \
        --provider "$PROVIDER"

    CONTAINER_EXIT_CODE=$?

    if [ $CONTAINER_EXIT_CODE -eq 0 ]; then
        echo "Container $CONTAINER_NAME completed successfully"
    else
        echo "Container $CONTAINER_NAME exited with status $CONTAINER_EXIT_CODE"
    fi

    # Copy files from container to host
    echo "Copying files from container to host..."
    docker cp "$CONTAINER_NAME:/app/." "$HOST_OUTPUT_DIR"
    echo "Files copied to $HOST_OUTPUT_DIR"

    # Remove the container
    echo "Removing the container..."
    docker rm "$CONTAINER_NAME"
}

# Main script logic
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <image_name> <prompt> <provider> <gpu_ids> <huggingface_token> <env_file_path>"
    exit 1
fi

IMAGE_NAME="$1"
PROMPT="$2"
PROVIDER="$3"
GPU_IDS="$4"
HUGGINGFACE_TOKEN="$5"
ENV_FILE_PATH="$6"

echo "IMAGE_NAME: $IMAGE_NAME"
echo "PROMPT: $PROMPT"
echo "PROVIDER: $PROVIDER"
echo "GPU_IDS: $GPU_IDS"
echo "HUGGINGFACE_TOKEN: $HUGGINGFACE_TOKEN"
echo "ENV_FILE_PATH: $ENV_FILE_PATH"

# Pull the image
pull_image "$IMAGE_NAME"

# Run the container
run_container "$IMAGE_NAME" "$PROMPT" "$PROVIDER" "$GPU_IDS" "$HUGGINGFACE_TOKEN" "$ENV_FILE_PATH"

