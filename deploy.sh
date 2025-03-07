#!/bin/bash

# Set variables
PROJECT_ID="challenge-452921"
REGION="us-central1"
REPOSITORY="challenge"
IMAGE_NAME="challenge-image"
TAG="latest"
JOB_NAME="challenge-job"
SERVICE_ACCOUNT="challenge@challenge-452921.iam.gserviceaccount.com"

# Enable required services
gcloud services enable artifactregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable iam.googleapis.com

# Authenticate Docker to push to Google Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev

# Create Artifact Registry (if it doesn't exist)
gcloud artifacts repositories create $REPOSITORY --repository-format=docker --location=$REGION --description="Docker repository" || true

# Build the Docker image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG .

# Push the image to Google Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME:$TAG

# Grant 'iam.serviceAccountUser' role to the current user
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT \
    --member="user:$(gcloud config get-value core/account)" \
    --role="roles/iam.serviceAccountUser" \
    --project=$PROJECT_ID

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
