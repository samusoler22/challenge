#!/bin/bash

# Set variables
PROJECT_ID="challenge-452921"
REGION="us-central1"
REPOSITORY="challenge"
IMAGE_NAME="challenge-image"
TAG="latest"
JOB_NAME="challenge-job"
SERVICE_ACCOUNT="challenge@challenge-452921.iam.gserviceaccount.com"

#Select project
gcloud config set project $PROJECT_ID

#Select active account
gcloud auth activate-service-account --key-file=gc_user.json

# Enable required services
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable iam.googleapis.com

# Authenticate Docker to push to Google Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev --quiet

# Create Artifact Registry (if it doesn't exist)
gcloud artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION --description="Docker repository" || true --quiet

# Build the Docker image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG .

# Push the image to Google Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG

# Delete the existing job
gcloud run jobs delete $JOB_NAME --region $REGION --quiet

# Deploy to Cloud Run Job
gcloud run jobs create $JOB_NAME \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG \
  --region $REGION \
  --task-timeout=1200s \
  --max-retries=3 \
  --service-account=$SERVICE_ACCOUNT \
  --memory=2Gi

# Run the Cloud Run Job
gcloud run jobs execute $JOB_NAME --region $REGION

echo "✅ Cloud Run Job deployed and executed!"
