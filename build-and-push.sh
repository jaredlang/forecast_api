#!/bin/bash
set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="weather-forecast-api"
TAG="${TAG:-latest}"
IMAGE_PATH="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${TAG}"

echo "================================================"
echo "Building Docker image"
echo "================================================"
echo "Project ID: ${PROJECT_ID}"
echo "Service Name: ${SERVICE_NAME}"
echo "Tag: ${TAG}"
echo "Image Path: ${IMAGE_PATH}"
echo "================================================"

# Build the image
docker build -t "$IMAGE_PATH" .

echo "Pushing image to Google Container Registry..."
docker push "$IMAGE_PATH"

echo "================================================"
echo "Build and push completed successfully!"
echo "Image: ${IMAGE_PATH}"
echo "================================================"
echo ""
echo "Now run ./deploy-cloudrun.sh to deploy this image to Cloud Run"
