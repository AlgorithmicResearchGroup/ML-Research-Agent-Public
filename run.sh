#!/bin/bash

# Function to pull the Docker image if it's not already on the machine
pull_image() {
    local IMAGE_NAME=$1
    if ! docker image inspect $IMAGE_NAME >/dev/null 2>&1; then
        echo "Image $IMAGE_NAME not found locally. Pulling from Docker Hub..."
        docker pull $IMAGE_NAME
    else
        echo "Image $IMAGE_NAME already exists locally."
    fi
}

# Function to run the Docker container with a 2-hour time limit
# Function to run the Docker container
run_container() {
    if [ "$#" -ne 8 ]; then
        echo "Usage: run_container <image_name> <prompt> <provider> <gpu_ids> <huggingface_token> <env_file_path>"
        echo "Example: run_container algorithmicresearch/agent:latest 'write an article on the history of python' openai 0 hf_token /home/ubuntu/.env"
        return 1
    fi
    IMAGE_NAME="$1"
    BENCHMARK="$2"
    PROMPT="$3"
    PROVIDER="$4"
    GPU_IDS="$5"
    HUGGINGFACE_TOKEN="$6"
    ENV_FILE_PATH="$7"

    echo "IMAGE_NAME: $IMAGE_NAME"
    echo "PROMPT: $PROMPT"
    echo "PROVIDER: $PROVIDER"
    echo "GPU_IDS: $GPU_IDS"
    echo "HUGGINGFACE_TOKEN: $HUGGINGFACE_TOKEN"
    echo "ENV_FILE_PATH: $ENV_FILE_PATH"

    CONTAINER_NAME="agent_${PROVIDER}_$(date +%Y%m%d_%H%M%S)"
    HOST_OUTPUT_DIR="/home/ubuntu/agent_output/${CONTAINER_NAME}"

    # Ensure the host output directory exists
    mkdir -p "$HOST_OUTPUT_DIR"
    #timeout $TIME_LIMIT docker run -it \


    docker run -it \
        --name $CONTAINER_NAME \
        --gpus "device=$GPU_IDS" \
        -e NVIDIA_VISIBLE_DEVICES=$GPU_IDS \
        -e BENCHMARK=$BENCHMARK \
        -e PROVIDER=$PROVIDER \
        -e TASK_NAME=$TASK_NAME \
        -e HUGGINGFACE_TOKEN=$HUGGINGFACE_TOKEN \
        -v "$HOST_OUTPUT_DIR:/app/output" \
        --env-file $ENV_FILE_PATH \
        -v $ENV_FILE_PATH:/app/.env \
        $IMAGE_NAME

    DOCKER_PID=$!

    wait $DOCKER_PID
    CONTAINER_EXIT_CODE=$?

    if [ $CONTAINER_EXIT_CODE -eq 0 ]; then
        echo "Container $CONTAINER_NAME completed successfully"
    elif [ $CONTAINER_EXIT_CODE -eq 124 ]; then
        echo "Container $CONTAINER_NAME was terminated after reaching the 2-hour time limit"
    else
        echo "Container $CONTAINER_NAME exited with status $CONTAINER_EXIT_CODE"
    fi

    # Copy files from container to host
    echo "Copying files from container to host..."
    docker cp $CONTAINER_NAME:/app/. "$HOST_OUTPUT_DIR"
    echo "Files copied to $HOST_OUTPUT_DIR"

    # Remove the container
    echo "Removing the container..."
    docker rm $CONTAINER_NAME
}

# Main script logic
if [ "$#" -ne 8 ]; then
    echo "Usage: $0 <image_name> <prompt> <provider> <gpu_ids> <huggingface_token> <env_file_path>"
    exit 1
fi

IMAGE_NAME="$1"
BENCHMARK="$2"
PROMPT="$3"
PROVIDER="$4"
GPU_IDS="$5"
HUGGINGFACE_TOKEN="$6"
ENV_FILE_PATH="$7"

# Pull the image
pull_image "$IMAGE_NAME"

# Run the container
run_container "$IMAGE_NAME" "$PROMPT" "$PROVIDER" "$GPU_IDS" "$HUGGINGFACE_TOKEN" "$ENV_FILE_PATH"

