#!/bin/bash

# Setup Workload Identity Federation for GitHub Actions
# Run this script with your GCP project ID as an argument

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <PROJECT_ID>"
    echo "Example: $0 my-trainflow-project"
    exit 1
fi

PROJECT_ID=$1
REPO_OWNER="trinchetto"  # Replace with your GitHub username/org
REPO_NAME="TrainFlow-AI"
POOL_ID="github-actions-pool"
PROVIDER_ID="github-actions-provider"
SERVICE_ACCOUNT="github-actions-sa"

echo "Setting up Workload Identity Federation for project: $PROJECT_ID"
echo "Repository: $REPO_OWNER/$REPO_NAME"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable iamcredentials.googleapis.com
gcloud services enable sts.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create a service account for GitHub Actions
echo "Creating service account..."
if gcloud iam service-accounts describe $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com >/dev/null 2>&1; then
    echo "Service account $SERVICE_ACCOUNT already exists, skipping creation"
else
    gcloud iam service-accounts create $SERVICE_ACCOUNT \
        --display-name="GitHub Actions Service Account" \
        --description="Service account for GitHub Actions deployments"
fi

# Grant necessary roles to the service account
echo "Granting roles to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create workload identity pool
echo "Creating workload identity pool..."
if gcloud iam workload-identity-pools describe $POOL_ID --location="global" >/dev/null 2>&1; then
    echo "Workload identity pool $POOL_ID already exists, skipping creation"
else
    gcloud iam workload-identity-pools create $POOL_ID \
        --location="global" \
        --display-name="GitHub Actions Pool" \
        --description="Identity pool for GitHub Actions"
fi

# Get the full ID of the workload identity pool
WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools describe $POOL_ID \
    --location="global" \
    --format="value(name)")

# Create workload identity provider
echo "Creating workload identity provider..."
if gcloud iam workload-identity-pools providers describe $PROVIDER_ID --location="global" --workload-identity-pool=$POOL_ID >/dev/null 2>&1; then
    echo "Workload identity provider $PROVIDER_ID already exists, skipping creation"
else
    gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID \
        --location="global" \
        --workload-identity-pool=$POOL_ID \
        --display-name="GitHub Actions Provider" \
        --issuer-uri="https://token.actions.githubusercontent.com" \
        --attribute-mapping="google.subject=assertion.sub"
fi

# Allow GitHub Actions to impersonate the service account
echo "Setting up impersonation..."
gcloud iam service-accounts add-iam-policy-binding \
    $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/$WORKLOAD_IDENTITY_POOL_ID/*"

# Get the workload identity provider name
WORKLOAD_IDENTITY_PROVIDER=$(gcloud iam workload-identity-pools providers describe $PROVIDER_ID \
    --location="global" \
    --workload-identity-pool=$POOL_ID \
    --format="value(name)")

echo ""
echo "🎉 Workload Identity Federation setup complete!"
echo ""
echo "Add these secrets to your GitHub repository ($REPO_OWNER/$REPO_NAME):"
echo "Settings > Secrets and variables > Actions > Repository secrets"
echo ""
echo "WIF_PROVIDER: $WORKLOAD_IDENTITY_PROVIDER"
echo "WIF_SERVICE_ACCOUNT: $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"
echo "GCP_PROJECT_ID: $PROJECT_ID"
echo ""
echo "You can also set these environment variables for testing:"
echo "export WIF_PROVIDER='$WORKLOAD_IDENTITY_PROVIDER'"
echo "export WIF_SERVICE_ACCOUNT='$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com'"