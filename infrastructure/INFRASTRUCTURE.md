# Infrastructure - Azure Resource Setup

> **Status: ✅ COMPLETE** (January 11, 2026)

---

## Resource Inventory (Deployed)

| Resource | Name | Location | Status |
|----------|------|----------|--------|
| Resource Group | `rg-ai-foundry-learning` | - | ✅ Active |
| Azure OpenAI | `openai-stihl-analytics` | West US | ✅ Deployed |
| ADLS Gen2 | `adlsstihlanalytics` | West US | ✅ Deployed |
| Databricks | `dbw-stihl-analytics` | West US | ✅ Deployed |
| AI Foundry | `stihl-analytics-agent` | West US 2 | ✅ Deployed |
| Access Connector | `dbw-stihl-access-connector` | West US | ✅ Deployed |

---

## Endpoints

| Service | Endpoint |
|---------|----------|
| Azure OpenAI | `https://openai-stihl-analytics.openai.azure.com/` |
| ADLS DFS | `https://adlsstihlanalytics.dfs.core.windows.net/` |
| ADLS Blob | `https://adlsstihlanalytics.blob.core.windows.net/` |
| Databricks | `https://adb-7405610757175308.8.azuredatabricks.net` |
| AI Foundry | `https://stihl-analytics-agent-resource.services.ai.azure.com/` |

---

## Model Deployments

| Deployment | Model | TPM | Purpose |
|------------|-------|-----|---------|
| `gpt-4o-mini` | gpt-4o-mini | 30K | Agent reasoning |
| `text-embedding-ada-002` | text-embedding-ada-002 | 30K | Vector embeddings |

---

## Storage Configuration

### ADLS Gen2: `adlsstihlanalytics`

| Setting | Value |
|---------|-------|
| Account Type | StorageV2 |
| Hierarchical Namespace | Enabled |
| Container | `stihl-analytics-data` |
| Replication | LRS |

### Medallion Directories
```
stihl-analytics-data/
├── bronze/
│   ├── products_raw/
│   ├── dealers_raw/
│   ├── sales_raw/
│   └── inventory_raw/
├── silver/
└── gold/
```

---

## Security Configuration

### Managed Identity (Secure ADLS Access)

| Component | Value |
|-----------|-------|
| Access Connector | `dbw-stihl-access-connector` |
| Principal ID | `1a40f23e-a4a2-4e39-8e88-be8038f99152` |
| Role | Storage Blob Data Contributor |
| Scope | `adlsstihlanalytics` storage account |

### Databricks External Location

| Setting | Value |
|---------|-------|
| Name | `stihl_adls_location` |
| Credential | `stihl_adls_credential` |
| URL | `abfss://stihl-analytics-data@adlsstihlanalytics.dfs.core.windows.net/` |
| Permissions | Read, List, Write, Delete ✅ |

---

## Environment Variables (.env)

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://openai-stihl-analytics.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-api-key>
AZURE_OPENAI_DEPLOYMENT_GPT=gpt-4o-mini
AZURE_OPENAI_DEPLOYMENT_EMBEDDING=text-embedding-ada-002

# Azure AI Foundry
FOUNDRY_PROJECT_ENDPOINT=https://stihl-analytics-agent-resource.services.ai.azure.com/

# Azure Data Lake Storage Gen2
ADLS_ACCOUNT_NAME=adlsstihlanalytics
ADLS_CONTAINER=stihl-analytics-data
ADLS_CONNECTION_STRING=<your-connection-string>
ADLS_DFS_ENDPOINT=https://adlsstihlanalytics.dfs.core.windows.net/

# Azure Databricks
DATABRICKS_WORKSPACE_URL=https://adb-7405610757175308.8.azuredatabricks.net
DATABRICKS_TOKEN=<generate-pat-token>
GENIE_SPACE_ID=<create-after-setup>

# Azure Resource Info
AZURE_RESOURCE_GROUP=rg-ai-foundry-learning
AZURE_LOCATION=westus
```

---

## Setup Commands (Reference)

### Azure OpenAI
```powershell
# Create resource
az cognitiveservices account create `
  --name openai-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --location westus `
  --kind OpenAI `
  --sku S0

# Deploy models
az cognitiveservices account deployment create `
  --name openai-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --deployment-name gpt-4o-mini `
  --model-name gpt-4o-mini `
  --model-version "2024-07-18" `
  --model-format OpenAI `
  --sku-capacity 30 `
  --sku-name Standard
```

### ADLS Gen2
```powershell
# Create storage
az storage account create `
  --name adlsstihlanalytics `
  --resource-group rg-ai-foundry-learning `
  --location westus `
  --sku Standard_LRS `
  --kind StorageV2 `
  --hns true

# Create container and directories
az storage container create --name stihl-analytics-data ...
```

### Databricks
```powershell
az databricks workspace create `
  --name dbw-stihl-analytics `
  --resource-group rg-ai-foundry-learning `
  --location westus `
  --sku premium
```

### Access Connector (Managed Identity)
```powershell
# Create connector
az databricks access-connector create `
  --name "dbw-stihl-access-connector" `
  --resource-group rg-ai-foundry-learning `
  --location westus `
  --identity-type SystemAssigned

# Assign RBAC role
az role assignment create `
  --assignee "1a40f23e-a4a2-4e39-8e88-be8038f99152" `
  --role "Storage Blob Data Contributor" `
  --scope "/subscriptions/f145b6d6-938e-4be9-876d-eac04dbda8e2/resourceGroups/rg-ai-foundry-learning/providers/Microsoft.Storage/storageAccounts/adlsstihlanalytics"
```

---

## Estimated Monthly Costs

| Resource | Estimate |
|----------|----------|
| Azure OpenAI | $5-15 |
| ADLS Gen2 | $2-5 |
| Databricks | $50-100 |
| AI Foundry | $5-10 |
| **Total** | **$60-130** |

---

## ✅ Setup Checklist (Completed)

- [x] Create resource group
- [x] Deploy Azure OpenAI with models
- [x] Create ADLS Gen2 with medallion structure
- [x] Create Databricks Premium workspace
- [x] Create AI Foundry standalone project
- [x] Configure Access Connector with managed identity
- [x] Assign RBAC roles for secure storage access
- [x] Create storage credential in Databricks
- [x] Create external location in Databricks
- [x] Test connection (all permissions confirmed)
- [x] Configure .env file

---

## Related Documents

- [PROJECT-MASTER.md](../PROJECT-MASTER.md) - Main project hub
- [DATA-LAYER.md](../data/DATA-LAYER.md) - Data architecture
- [DATABRICKS.md](../databricks/DATABRICKS.md) - Databricks setup

---

*Last Updated: January 12, 2026*
