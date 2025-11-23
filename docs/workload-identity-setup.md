# Workload Identity Federation Setup for TrainFlow AI

This guide helps you set up secure authentication between GitHub Actions and Google Cloud using Workload Identity Federation (WIF), eliminating the need for service account keys.

## Prerequisites

- Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- Admin access to your GitHub repository
- Owner or Editor role in the GCP project

## Step 1: Run the Setup Script

1. **Make sure you're authenticated with gcloud:**

   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Run the setup script:**

   ```bash
   ./scripts/setup_workload_identity.sh YOUR_PROJECT_ID
   ```
   
   Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

3. **The script will:**
   - Enable required Google Cloud APIs
   - Create a service account for GitHub Actions
   - Grant necessary permissions (Cloud Run, Cloud Build, Storage)
   - Create a Workload Identity Pool and Provider
   - Configure the identity federation

## Step 2: Configure GitHub Secrets

After running the setup script, add these secrets to your GitHub repository:

**Go to:** `Settings` > `Secrets and variables` > `Actions` > `Repository secrets`

**Add these secrets:**

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `WIF_PROVIDER` | Workload Identity Provider ID | `projects/123456789/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider` |
| `WIF_SERVICE_ACCOUNT` | Service Account Email | `github-actions-sa@your-project.iam.gserviceaccount.com` |
| `GCP_PROJECT_ID` | Your GCP Project ID | `your-project-id` |
| `CLOUD_RUN_REGION` | Region for Cloud Run deployment | `us-central1` |
| `CLOUD_RUN_SERVICE` | Cloud Run service name | `trainflow-ai` |
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |

> **Note:** The setup script will output the exact values you need for `WIF_PROVIDER` and `WIF_SERVICE_ACCOUNT`.

## Step 3: Test the Deployment

1. **Push to main branch** to trigger the deployment:

   ```bash
   git add .
   git commit -m "Setup Workload Identity Federation"
   git push origin main
   ```

2. **Monitor the GitHub Actions workflow** in the Actions tab of your repository.

3. **Verify the deployment** by checking your Cloud Run service in the Google Cloud Console.

## Security Benefits

✅ **No service account keys** stored in GitHub  
✅ **Short-lived tokens** that auto-expire  
✅ **Repository-scoped access** - only your specific repo can use the identity  
✅ **Audit trail** - all authentication events are logged  
✅ **Principle of least privilege** - service account has only necessary permissions  

## Troubleshooting

### Common Issues

1. **"Permission denied" errors:**
   - Ensure your service account has the correct roles
   - Check that the workload identity binding is correct

2. **"Identity pool not found":**
   - Make sure you ran the setup script successfully
   - Verify the WIF_PROVIDER secret is correct

3. **"Repository not authorized":**
   - Ensure the repository name in the setup script matches exactly (case-sensitive)
   - Check the attribute mapping includes your repository

### Debug Commands

```bash
# Check service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID --flatten="bindings[].members" --filter="bindings.members:github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com"

# List workload identity pools
gcloud iam workload-identity-pools list --location=global

# Describe the identity pool
gcloud iam workload-identity-pools describe github-actions-pool --location=global
```

## Cleanup (if needed)

To remove the Workload Identity Federation setup:

```bash
# Delete the workload identity pool (this also removes the provider)
gcloud iam workload-identity-pools delete github-actions-pool --location=global

# Delete the service account
gcloud iam service-accounts delete github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

