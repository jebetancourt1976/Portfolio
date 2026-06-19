# Azure Container Apps Deployment Plan
## Multi-Policy RAG Orchestrator

**Last Updated**: 2026-06-04  
**Status**: Ready for Implementation

---

## 📋 Executive Summary

This plan deploys the Multi-Policy RAG Orchestrator to **Azure Container Apps** - a fully managed, serverless container platform that provides:

- ✅ **No Kubernetes/VM management** - Fully serverless
- ✅ **Automatic scaling** - Scale to zero when idle
- ✅ **Built-in TLS/HTTPS** - Automatic certificate management
- ✅ **Public HTTPS URL** - Accessible from anywhere
- ✅ **Pay-per-use pricing** - Only pay for actual usage

**Estimated Cost**: $0.05 - $0.15 per hour (typical usage)  
**Deployment Time**: 15-20 minutes

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet (HTTPS)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Azure Container Apps Environment                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Container App: multi-policy-rag                      │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Docker Image from ACR                          │  │  │
│  │  │  - Gradio UI (Port 7860)                        │  │  │
│  │  │  - RAG Orchestrator                             │  │  │
│  │  │  - FAISS Indexes (Azure Files)                  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  Auto-scaling: 0-10 replicas                          │  │
│  │  CPU: 0.5 cores, Memory: 1 GB                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Built-in Features:                                         │
│  • Automatic TLS/SSL certificates                           │
│  • Load balancing                                           │
│  • Health monitoring                                        │
│  • Log Analytics integration                                │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Azure Container Registry (ACR)                     │
│  • Stores Docker images                                     │
│  • Private registry                                         │
│  • Geo-replication available                                │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          Azure Files (Optional)                             │
│  • Persistent storage for FAISS indexes                     │
│  • Shared across container instances                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Prerequisites

### Required Azure Resources
- ✅ Active Azure subscription
- ✅ Azure CLI installed locally
- ✅ Docker installed locally
- ✅ OpenAI API key

### Required Permissions
- Contributor role on the subscription or resource group
- Ability to create:
  - Resource Groups
  - Container Registries
  - Container Apps
  - Storage Accounts (optional)

---

## 🚀 Deployment Steps

### Step 1: Prepare Local Environment

```bash
# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Install Container Apps extension
az extension add --name containerapp --upgrade

# Set environment variables
export RESOURCE_GROUP="rg-multi-policy-rag"
export LOCATION="eastus"
export ACR_NAME="acrmultipolicyrag"  # Must be globally unique, lowercase, no hyphens
export CONTAINER_APP_ENV="env-multi-policy-rag"
export CONTAINER_APP_NAME="multi-policy-rag"
export IMAGE_NAME="multi-policy-rag-orchestrator"
export IMAGE_TAG="v1.0.0"
```

### Step 2: Create Resource Group

```bash
# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Expected output: Resource group created successfully
```

### Step 3: Create Azure Container Registry (ACR)

```bash
# Create ACR (Basic tier for cost optimization)
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show \
  --name $ACR_NAME \
  --query loginServer \
  --output tsv)

echo "ACR Login Server: $ACR_LOGIN_SERVER"

# Expected output: acrmultipolicyrag.azurecr.io
```

### Step 4: Build and Push Docker Image

```bash
# Navigate to project directory
cd c:/Users/jebet/OneDrive/MachineLearningTCAE/RAGS

# Login to ACR
az acr login --name $ACR_NAME

# Build Docker image locally
docker build -t $IMAGE_NAME:$IMAGE_TAG .

# Tag image for ACR
docker tag $IMAGE_NAME:$IMAGE_TAG $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG

# Push image to ACR
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG

# Verify image in ACR
az acr repository list --name $ACR_NAME --output table

# Expected output: multi-policy-rag-orchestrator
```

**Alternative: Build directly in ACR (recommended for slower connections)**

```bash
# Build in Azure (no local Docker build needed)
az acr build \
  --registry $ACR_NAME \
  --image $IMAGE_NAME:$IMAGE_TAG \
  --file Dockerfile \
  .

# This uploads source code and builds in Azure
```

### Step 5: Create Container Apps Environment

```bash
# Create Container Apps environment
az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Expected output: Environment created successfully
```

### Step 6: Create Azure Files Storage (Optional - for persistent FAISS indexes)

```bash
# Create storage account
STORAGE_ACCOUNT="stmultipolicyrag"  # Must be globally unique, lowercase, no hyphens

az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# Create file share for FAISS indexes
az storage share create \
  --name faiss-indexes \
  --account-name $STORAGE_ACCOUNT \
  --quota 10

# Get storage account key
STORAGE_KEY=$(az storage account keys list \
  --account-name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query "[0].value" \
  --output tsv)

# Add storage to Container Apps environment
az containerapp env storage set \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --storage-name faiss-storage \
  --azure-file-account-name $STORAGE_ACCOUNT \
  --azure-file-account-key $STORAGE_KEY \
  --azure-file-share-name faiss-indexes \
  --access-mode ReadWrite
```

### Step 7: Deploy Container App

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show \
  --name $ACR_NAME \
  --query username \
  --output tsv)

ACR_PASSWORD=$(az acr credential show \
  --name $ACR_NAME \
  --query "passwords[0].value" \
  --output tsv)

# Create Container App
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 7860 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --env-vars \
    "OPENAI_API_KEY=secretref:openai-api-key" \
    "LLM_MODEL=gpt-4o-mini" \
    "EMBED_MODEL=text-embedding-3-small" \
    "GRADIO_SERVER_NAME=0.0.0.0" \
    "GRADIO_SERVER_PORT=7860" \
    "CHUNK_SIZE=800" \
    "CHUNK_OVERLAP=100" \
    "TOP_K=4" \
  --secrets \
    "openai-api-key=YOUR_OPENAI_API_KEY_HERE"

# Expected output: Container app created successfully
```

**With Azure Files storage mount:**

```bash
az containerapp create \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 7860 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 10 \
  --env-vars \
    "OPENAI_API_KEY=secretref:openai-api-key" \
    "LLM_MODEL=gpt-4o-mini" \
    "EMBED_MODEL=text-embedding-3-small" \
    "GRADIO_SERVER_NAME=0.0.0.0" \
    "GRADIO_SERVER_PORT=7860" \
    "CHUNK_SIZE=800" \
    "CHUNK_OVERLAP=100" \
    "TOP_K=4" \
  --secrets \
    "openai-api-key=YOUR_OPENAI_API_KEY_HERE" \
  --volume-mount \
    "faiss-storage:/app/data/faiss_indexes"
```

### Step 8: Get Application URL

```bash
# Get the FQDN (Fully Qualified Domain Name)
APP_URL=$(az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Application URL: https://$APP_URL"

# Expected output: https://multi-policy-rag.proudhill-12345678.eastus.azurecontainerapps.io
```

### Step 9: Verify Deployment

```bash
# Check container app status
az containerapp show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query "properties.runningStatus" \
  --output tsv

# View logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Test the application
curl https://$APP_URL
```

---

## 🔄 Update Deployment (CI/CD)

### Manual Update

```bash
# Build new version
docker build -t $IMAGE_NAME:v1.0.1 .
docker tag $IMAGE_NAME:v1.0.1 $ACR_LOGIN_SERVER/$IMAGE_NAME:v1.0.1
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:v1.0.1

# Update container app
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image $ACR_LOGIN_SERVER/$IMAGE_NAME:v1.0.1
```

### Automated CI/CD with GitHub Actions

Create `.github/workflows/azure-deploy.yml`:

```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  AZURE_RESOURCE_GROUP: rg-multi-policy-rag
  ACR_NAME: acrmultipolicyrag
  CONTAINER_APP_NAME: multi-policy-rag
  IMAGE_NAME: multi-policy-rag-orchestrator

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Build and push to ACR
        run: |
          az acr build \
            --registry ${{ env.ACR_NAME }} \
            --image ${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --image ${{ env.IMAGE_NAME }}:latest \
            --file Dockerfile \
            .

      - name: Deploy to Container Apps
        run: |
          az containerapp update \
            --name ${{ env.CONTAINER_APP_NAME }} \
            --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
            --image ${{ env.ACR_NAME }}.azurecr.io/${{ env.IMAGE_NAME }}:${{ github.sha }}
```

---

## 💰 Cost Estimation

### Azure Container Apps Pricing (East US)

**Consumption Plan** (Pay-per-use):

| Resource | Unit | Price | Usage | Monthly Cost |
|----------|------|-------|-------|--------------|
| vCPU | per vCPU-second | $0.000024 | 0.5 vCPU × 720 hrs | $31.10 |
| Memory | per GiB-second | $0.000003 | 1 GB × 720 hrs | $7.78 |
| HTTP Requests | per million | $0.40 | 100K requests | $0.04 |
| **Subtotal** | | | | **$38.92/month** |

**With Scale-to-Zero** (Typical usage: 8 hours/day):

| Resource | Monthly Cost |
|----------|--------------|
| Active time (8 hrs/day) | $12.97 |
| Idle time (scaled to 0) | $0.00 |
| HTTP Requests | $0.04 |
| **Total** | **~$13/month** |

### Azure Container Registry

| Tier | Storage | Price/Month |
|------|---------|-------------|
| Basic | 10 GB | $5.00 |

### Azure Files (Optional)

| Resource | Size | Price/Month |
|----------|------|-------------|
| File Storage | 10 GB | $2.00 |

### OpenAI API Costs (Estimated)

| Model | Usage | Cost/Month |
|-------|-------|------------|
| GPT-4o-mini | 1M tokens | $0.15 - $0.60 |
| text-embedding-3-small | 1M tokens | $0.02 |
| **Total** | | **$0.17 - $0.62** |

### **Total Monthly Cost Estimate**

| Scenario | Cost/Month | Cost/Hour |
|----------|------------|-----------|
| **Always On (24/7)** | $44 - $47 | $0.06 - $0.07 |
| **Typical Usage (8hrs/day)** | $20 - $23 | $0.08 - $0.10 (active) |
| **Light Usage (2hrs/day)** | $10 - $13 | $0.17 - $0.22 (active) |

**Cost Optimization Tips:**
- ✅ Enable scale-to-zero (min replicas = 0)
- ✅ Use Basic ACR tier
- ✅ Use gpt-4o-mini instead of gpt-4
- ✅ Implement request caching
- ✅ Set appropriate max replicas

---

## 🔒 Security Best Practices

### 1. Secure Secrets Management

```bash
# Use Azure Key Vault for secrets
az keyvault create \
  --name kv-multi-policy-rag \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Store OpenAI API key
az keyvault secret set \
  --vault-name kv-multi-policy-rag \
  --name openai-api-key \
  --value "YOUR_OPENAI_API_KEY"

# Grant Container App access to Key Vault
# (Requires managed identity setup)
```

### 2. Network Security

```bash
# Restrict ingress to specific IPs (optional)
az containerapp ingress access-restriction set \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --rule-name "office-ip" \
  --ip-address "203.0.113.0/24" \
  --action Allow
```

### 3. Enable Authentication (Optional)

```bash
# Enable Azure AD authentication
az containerapp auth update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --enabled true \
  --action RedirectToLoginPage \
  --aad-client-id "YOUR_AAD_CLIENT_ID" \
  --aad-client-secret "YOUR_AAD_CLIENT_SECRET"
```

---

## 📊 Monitoring and Logging

### View Logs

```bash
# Real-time logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --follow

# Recent logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 100
```

### Metrics

```bash
# View metrics in Azure Portal
# Navigate to: Container App > Monitoring > Metrics

# Available metrics:
# - Requests
# - CPU usage
# - Memory usage
# - Replica count
# - Response time
```

### Application Insights (Optional)

```bash
# Create Application Insights
az monitor app-insights component create \
  --app multi-policy-rag-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP

# Get instrumentation key
APPINSIGHTS_KEY=$(az monitor app-insights component show \
  --app multi-policy-rag-insights \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

# Update container app with Application Insights
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --set-env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=$APPINSIGHTS_KEY"
```

---

## 🔧 Scaling Configuration

### Auto-scaling Rules

```bash
# HTTP-based scaling
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 0 \
  --max-replicas 10 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50

# CPU-based scaling
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --scale-rule-name cpu-rule \
  --scale-rule-type cpu \
  --scale-rule-metadata "type=Utilization" "value=70"
```

### Resource Limits

```bash
# Update CPU and memory
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --cpu 1.0 \
  --memory 2.0Gi
```

---

## 🧪 Testing

### Health Check

```bash
# Test application endpoint
curl https://$APP_URL

# Expected: Gradio UI HTML response
```

### Load Testing

```bash
# Install Apache Bench
# Windows: Download from Apache website
# Linux: sudo apt-get install apache2-utils

# Run load test
ab -n 1000 -c 10 https://$APP_URL/
```

---

## 🗑️ Cleanup

### Delete All Resources

```bash
# Delete resource group (removes all resources)
az group delete \
  --name $RESOURCE_GROUP \
  --yes \
  --no-wait

# Verify deletion
az group list --output table
```

### Delete Individual Resources

```bash
# Delete container app
az containerapp delete \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --yes

# Delete container registry
az acr delete \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --yes

# Delete storage account
az storage account delete \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --yes
```

---

## 📝 Troubleshooting

### Issue: Container fails to start

**Solution:**
```bash
# Check logs
az containerapp logs show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --tail 100

# Check revision status
az containerapp revision list \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --output table
```

### Issue: Cannot pull image from ACR

**Solution:**
```bash
# Verify ACR credentials
az acr credential show --name $ACR_NAME

# Update container app with correct credentials
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD
```

### Issue: Application not accessible

**Solution:**
```bash
# Check ingress configuration
az containerapp ingress show \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP

# Ensure external ingress is enabled
az containerapp ingress enable \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --type external \
  --target-port 7860
```

### Issue: High costs

**Solution:**
```bash
# Enable scale-to-zero
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 0

# Reduce max replicas
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --max-replicas 3

# Reduce CPU/memory
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --cpu 0.25 \
  --memory 0.5Gi
```

---

## 🎯 Next Steps

1. ✅ **Deploy to Azure** - Follow steps 1-9
2. ✅ **Test application** - Verify functionality
3. ✅ **Set up monitoring** - Enable Application Insights
4. ✅ **Configure CI/CD** - Automate deployments
5. ✅ **Optimize costs** - Enable scale-to-zero
6. ✅ **Add custom domain** - Configure DNS (optional)
7. ✅ **Enable authentication** - Secure access (optional)

---

## 📚 Additional Resources

- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Container Registry Documentation](https://learn.microsoft.com/en-us/azure/container-registry/)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [Container Apps Samples](https://github.com/Azure-Samples/container-apps-samples)

---

## 📧 Support

For issues with this deployment plan:
- Review troubleshooting section
- Check Azure Container Apps documentation
- Open an issue on GitHub

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-04  
**Status**: Production Ready ✅