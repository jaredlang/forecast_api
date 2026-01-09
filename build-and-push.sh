#!/bin/bash
set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="weather-forecast-api"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Building Docker image..."
echo "Project ID: $PROJECT_ID"
echo "Image: $IMAGE_NAME"

# Build the image
docker build -t "$IMAGE_NAME:latest" .

echo "Pushing image to Google Container Registry..."
docker push "$IMAGE_NAME:latest"

echo ""
echo "Build and push complete!"
echo "Image: $IMAGE_NAME:latest"
echo ""
echo "Now run ./deploy-cloudrun.sh to deploy this image to Cloud Run"
