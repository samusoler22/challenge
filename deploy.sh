#!/bin/bash

# Set variables
PROJECT_ID="challenge-452921"        # Replace with your Google Cloud Project ID
REGION="us-central1"                 # Choose a Google Cloud region
REPOSITORY="challenge"               # Name for your Artifact Registry repository
IMAGE_NAME="challenge-image"         # Docker image name
TAG="latest"                         # Image tag

# Enable required services
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com

# Authenticate Docker to push to Google Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev

# Create Artifact Registry (if it doesn't exist)
gcloud artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION --description="Docker repository"

# Build the Docker image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG .

# Push the image to Google Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG

# Deploy to Cloud Run
gcloud run deploy $IMAGE_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1

echo "🚀 Deployment complete! Your service is live."

