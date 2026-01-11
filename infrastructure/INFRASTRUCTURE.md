# Infrastructure - Azure Resource Setup

> **Parent**: [PROJECT-MASTER.md](../PROJECT-MASTER.md)  
> **Status**: 🔄 Active  
> **Owner**: Infrastructure & DevOps

---

## Overview

This document covers all Azure resource provisioning and configuration for the AI Analytics Agent.

**Region**: West US 2 (all resources co-located)  
**Resource Group**: `rg-ai-foundry-learning`

---

## Resource Inventory

| Resource | Name | SKU/Tier | Purpose |
|----------|------|----------|---------|
| Azure OpenAI | `openai-stihl-analytics` | S0 | GPT-4o + Embeddings |
| ADLS Gen2 | `adlsstihlanalytics` | Standard_LRS | Medallion data storage |
| Databricks | `dbw-stihl-analytics` | Premium | Unity Catalog, Vector Search |
| AI Foundry | `stihl-analytics-agent` | Standalone | Agent orchestration |

---

## 1. Azure OpenAI Service

### 1.1 Resource Configuration

```yaml
Name: openai-stihl-analytics
Location: westus2
Kind: OpenAI
SKU: S0
Custom Domain: openai-stihl-analytics
```

### 1.2 Model Deployments

| Deployment Name | Model | Version | TPM |
|-----------------|-------|---------|-----|
| `gpt-4o` | gpt-4o | 2024-11-20 | 30K |
| `text-embedding-ada-002` | text-embedding-ada-002 | 2 | 30K |

### 1.3 Setup Commands

```powershell
# Create Azure OpenAI resource
az cognitiveservices account create `
  --name openai-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --location westus2 `
  --kind OpenAI `
  --sku S0 `
  --custom-domain openai-stihl-analytics

# Deploy GPT-4o
az cognitiveservices account deployment create `
  --name openai-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --deployment-name gpt-4o `
  --model-name gpt-4o `
  --model-version "2024-11-20" `
  --model-format OpenAI `
  --sku-capacity 30 `
  --sku-name Standard

# Deploy Embeddings
az cognitiveservices account deployment create `
  --name openai-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --deployment-name text-embedding-ada-002 `
  --model-name text-embedding-ada-002 `
  --model-version "2" `
  --model-format OpenAI `
  --sku-capacity 30 `
  --sku-name Standard
```

### 1.4 Retrieve Credentials

```powershell
# Get endpoint
az cognitiveservices account show `
  --name openai-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --query "properties.endpoint" -o tsv

# Get API key
az cognitiveservices account keys list `
  --name openai-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --query "key1" -o tsv
```

---

## 2. Azure Data Lake Storage Gen2

### 2.1 Resource Configuration

```yaml
Name: adlsstihlanalytics
Location: westus2
SKU: Standard_LRS
Kind: StorageV2
Hierarchical Namespace: Enabled (required for ADLS Gen2)
```

### 2.2 Container Structure

```
stihl-analytics-data/
├── bronze/          # Raw CSV/JSON files
├── silver/          # Cleaned Delta tables
└── gold/            # Aggregated Delta tables
```

### 2.3 Setup Commands

```powershell
# Create storage account
az storage account create `
  --name adlsstihlanalytics `
  --resource-group rg-ai-foundry-learning `
  --location westus2 `
  --sku Standard_LRS `
  --kind StorageV2 `
  --hns true

# Get storage key
$STORAGE_KEY = az storage account keys list `
  --account-name adlsstihlanalytics `
  --resource-group rg-ai-foundry-learning `
  --query "[0].value" -o tsv

# Create container
az storage container create `
  --name stihl-analytics-data `
  --account-name adlsstihlanalytics `
  --account-key $STORAGE_KEY

# Create medallion directories
foreach ($layer in @("bronze", "silver", "gold")) {
    az storage fs directory create `
      --name $layer `
      --file-system stihl-analytics-data `
      --account-name adlsstihlanalytics `
      --account-key $STORAGE_KEY
}
```

### 2.4 Connection String

```powershell
az storage account show-connection-string `
  --name adlsstihlanalytics `
  --resource-group rg-ai-foundry-learning `
  --query "connectionString" -o tsv
```

---

## 3. Azure Databricks

### 3.1 Resource Configuration

```yaml
Name: dbw-stihl-analytics
Location: westus2
SKU: Premium  # Required for Unity Catalog
```

### 3.2 Why Premium Tier?

| Feature | Standard | Premium |
|---------|----------|---------|
| Unity Catalog | ❌ | ✅ Required |
| Mosaic AI Vector Search | ❌ | ✅ Required |
| Row-level security | ❌ | ✅ |
| Audit logs | Limited | Full |

### 3.3 Setup Commands

```powershell
# Create Databricks workspace (takes 3-5 minutes)
az databricks workspace create `
  --name dbw-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --location westus2 `
  --sku premium

# Get workspace URL
az databricks workspace show `
  --name dbw-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --query "workspaceUrl" -o tsv
```

### 3.4 Post-Deployment Configuration

See [DATABRICKS.md](../databricks/DATABRICKS.md) for:
- Unity Catalog setup
- SQL Warehouse configuration
- Vector Search endpoint
- External Model endpoint

---

## 4. Azure AI Foundry (Standalone Project)

### 4.1 Critical Requirement

> ⚠️ **MUST use Standalone Project, NOT Hub-based**
> 
> The native Databricks connector requires `FOUNDRY_PROJECT_ENDPOINT` which is only exposed by standalone projects.

### 4.2 Portal Setup (Manual)

1. Navigate to [ai.azure.com](https://ai.azure.com)
2. Click **"+ New project"**
3. Select **"Create a new project"** (NOT "Add to existing hub")
4. Configure:
   - **Project name**: `stihl-analytics-agent`
   - **Resource group**: `rg-ai-foundry-learning`
   - **Location**: `West US 2`
5. Click **Create**

### 4.3 Verify Standalone Project

After creation:
1. Go to **Settings** → **Properties**
2. Confirm **"Project endpoint"** is visible
3. Copy endpoint URL for SDK configuration

### 4.4 Configure Connections

| Connection | Type | Configuration |
|------------|------|---------------|
| Azure OpenAI | API Key | Select `openai-stihl-analytics` |
| Databricks | PAT Token | Workspace URL + Genie Space ID |

---

## 5. Environment Configuration

### 5.1 .env File Template

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://openai-stihl-analytics.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT_GPT4O=gpt-4o
AZURE_OPENAI_DEPLOYMENT_EMBEDDING=text-embedding-ada-002

# Azure AI Foundry
FOUNDRY_PROJECT_ENDPOINT=https://stihl-analytics-agent.cognitiveservices.azure.com/

# Azure Data Lake Storage
ADLS_ACCOUNT_NAME=adlsstihlanalytics
ADLS_CONTAINER=stihl-analytics-data
ADLS_CONNECTION_STRING=<your-connection-string>

# Azure Databricks
DATABRICKS_WORKSPACE_URL=https://adb-xxxxx.azuredatabricks.net
DATABRICKS_TOKEN=<your-pat-token>
GENIE_SPACE_ID=<your-genie-space-id>

# General
AZURE_RESOURCE_GROUP=rg-ai-foundry-learning
AZURE_LOCATION=westus2
```

---

## 6. Cost Estimates

| Resource | Monthly Estimate |
|----------|------------------|
| Azure OpenAI | $20-50 |
| ADLS Gen2 (~10GB) | $2 |
| Databricks (Serverless SQL) | $50-100 |
| AI Foundry | $0 (pay per use) |
| **Total** | **$75-150** |

---

## ✅ Setup Checklist

- [ ] Azure OpenAI resource created
- [ ] GPT-4o model deployed
- [ ] Embedding model deployed
- [ ] ADLS Gen2 storage account created
- [ ] Container with medallion directories created
- [ ] Databricks Premium workspace created
- [ ] AI Foundry standalone project created
- [ ] Azure OpenAI connection configured
- [ ] Environment variables documented
- [ ] Credentials stored securely

---

## 🔗 Related Documents

- [DATABRICKS.md](../databricks/DATABRICKS.md) - Databricks workspace configuration
- [DATA-LAYER.md](../data/DATA-LAYER.md) - Storage structure and data flow
- [AGENT.md](../agent/AGENT.md) - AI Foundry agent setup

---

**Last Updated**: January 2026
