# GCP Cloud Logging Permission Fix

## Issue
The Google Guest Agent is experiencing permission denied errors when trying to write to Cloud Logging:

```
Cloud Logging Client Error: rpc error: code = PermissionDenied desc = Permission 'logging.logEntries.create' denied on resource '//logging.googleapis.com/projects/delta-surface-468416-f5/logs/GCEGuestAgent'
```

## Root Cause
The Cloud Resource Manager API is not enabled for project `300834760073`, and the service account `300834760073-compute@developer.gserviceaccount.com` lacks the necessary IAM permissions.

## Resolution Steps

### Option 1: Enable Cloud Resource Manager API (Recommended)
1. Visit: https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview?project=300834760073
2. Enable the Cloud Resource Manager API
3. Wait a few minutes for the changes to propagate
4. Add the necessary IAM permissions to the service account

### Option 2: Grant Service Account Logging Permissions
```bash
# Grant logging writer role to the compute service account
gcloud projects add-iam-policy-binding delta-surface-468416-f5 \
  --member="serviceAccount:300834760073-compute@developer.gserviceaccount.com" \
  --role="roles/logging.logWriter"

# Alternatively, grant the Logs Writer role at the instance level
gcloud compute instances add-iam-policy-binding et-gtw \
  --zone=us-central1-a \
  --member="serviceAccount:300834760073-compute@developer.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### Option 3: Disable Cloud Logging in Guest Agent
If Cloud Logging is not required, you can disable it by modifying the guest agent configuration:

```bash
# Edit guest agent configuration
sudo systemctl stop google-guest-agent-manager
sudo systemctl stop google-osconfig-agent

# This will stop the permission errors but also disable cloud logging
```

## Current Status
- Cloud Resource Manager API: **DISABLED**
- Service Account Permissions: **INSUFFICIENT**
- Recommended Action: **Enable API and grant permissions via GCP Console**

## Notes
This is a GCP infrastructure configuration issue that requires GCP console access or appropriate IAM permissions to resolve. The service account currently has full cloud-platform access but lacks the specific logging permissions.