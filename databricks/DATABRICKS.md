# Databricks - Unity Catalog, ETL & Vector Search

> **Parent**: [PROJECT-MASTER.md](../PROJECT-MASTER.md)  
> **Status**: ⏳ Pending  
> **Owner**: Data Engineering / MLOps

---

## Overview

This document covers Azure Databricks configuration including Unity Catalog, ETL notebooks, Mosaic AI Vector Search, and scheduled jobs.

**Workspace**: `dbw-stihl-analytics`  
**Tier**: Premium (required for Unity Catalog)  
**Region**: West US 2

---

## 1. Unity Catalog Structure

```
Unity Catalog
│
└── stihl_analytics (Catalog)
    │
    ├── bronze (Schema)
    │   ├── sales_raw
    │   ├── inventory_raw
    │   ├── products_raw
    │   └── dealers_raw
    │
    ├── silver (Schema)
    │   ├── sales
    │   ├── inventory
    │   ├── products
    │   ├── dealers
    │   ├── sales_vectorized
    │   ├── inventory_vectorized
    │   └── products_vectorized
    │
    └── gold (Schema)
        ├── sales_monthly
        ├── inventory_monthly
        ├── dealer_performance
        ├── sales_inv_combined
        ├── detected_anomalies
        ├── sales_forecasts
        ├── proactive_insights
        ├── sales_monthly_vectorized
        ├── insights_vectorized
        └── forecasts_vectorized
```

### 1.1 Create Catalog and Schemas

```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS stihl_analytics;
USE CATALOG stihl_analytics;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Grant permissions (for service principal)
GRANT ALL PRIVILEGES ON CATALOG stihl_analytics TO `ai-foundry-service`;
```

---

## 2. External Storage Location

Connect Unity Catalog to ADLS Gen2:

### 2.1 Create Storage Credential

```sql
-- Create storage credential (requires admin)
CREATE STORAGE CREDENTIAL adls_stihl_credential
WITH (
    AZURE_MANAGED_IDENTITY = '<managed-identity-id>'
);

-- Or with Service Principal
CREATE STORAGE CREDENTIAL adls_stihl_credential
WITH (
    AZURE_SERVICE_PRINCIPAL (
        DIRECTORY_ID = '<tenant-id>',
        APPLICATION_ID = '<app-id>',
        CLIENT_SECRET = '<secret>'
    )
);
```

### 2.2 Create External Location

```sql
CREATE EXTERNAL LOCATION stihl_data_location
URL 'abfss://stihl-analytics-data@adlsstihlanalytics.dfs.core.windows.net/'
WITH (STORAGE CREDENTIAL adls_stihl_credential);
```

---

## 3. SQL Warehouse

### 3.1 Configuration

| Setting | Value |
|---------|-------|
| **Name** | `stihl-analytics-warehouse` |
| **Type** | Serverless |
| **Size** | Small (starter) |
| **Auto Stop** | 10 minutes |
| **Scaling** | 1-2 clusters |

### 3.2 Create via UI

1. Go to **SQL Warehouses** in Databricks
2. Click **Create SQL Warehouse**
3. Select **Serverless**
4. Configure auto-stop for cost optimization

---

## 4. ETL Notebooks

Location: `databricks/notebooks/`

### 4.1 Notebook Pipeline

```
01_bronze_ingestion.py
        ↓
02_silver_transform.py
        ↓
03_gold_aggregation.py
        ↓
04_vectorization.py
        ↓
05_anomaly_detection.py
        ↓
06_forecasting.py
        ↓
07_insight_generation.py
```

### 4.2 01_bronze_ingestion.py

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Bronze Layer Ingestion
# MAGIC Load raw CSV/JSON files from ADLS into Bronze Delta tables

# COMMAND ----------
from pyspark.sql import SparkSession

# ADLS paths
BRONZE_PATH = "abfss://stihl-analytics-data@adlsstihlanalytics.dfs.core.windows.net/bronze"

# COMMAND ----------
# Load products
products_df = spark.read.json(f"{BRONZE_PATH}/products_raw/products.json")
products_df.write.format("delta").mode("overwrite").saveAsTable("stihl_analytics.bronze.products_raw")

# COMMAND ----------
# Load sales
sales_df = spark.read.option("header", True).csv(f"{BRONZE_PATH}/sales_raw/*.csv")
sales_df.write.format("delta").mode("overwrite").saveAsTable("stihl_analytics.bronze.sales_raw")

# COMMAND ----------
# Load inventory
inventory_df = spark.read.option("header", True).csv(f"{BRONZE_PATH}/inventory_raw/*.csv")
inventory_df.write.format("delta").mode("overwrite").saveAsTable("stihl_analytics.bronze.inventory_raw")

# COMMAND ----------
# Load dealers
dealers_df = spark.read.option("header", True).csv(f"{BRONZE_PATH}/dealers_raw/dealers.csv")
dealers_df.write.format("delta").mode("overwrite").saveAsTable("stihl_analytics.bronze.dealers_raw")
```

### 4.3 02_silver_transform.py

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Silver Layer Transformation
# MAGIC Clean, validate, and type-cast Bronze data

# COMMAND ----------
from pyspark.sql.functions import col, to_date, when, lit
from pyspark.sql.types import FloatType, IntegerType

# COMMAND ----------
# Transform sales
sales_bronze = spark.table("stihl_analytics.bronze.sales_raw")

sales_silver = (sales_bronze
    .withColumn("transaction_date", to_date(col("transaction_date")))
    .withColumn("quantity", col("quantity").cast(IntegerType()))
    .withColumn("unit_price", col("unit_price").cast(FloatType()))
    .withColumn("discount_pct", col("discount_pct").cast(FloatType()))
    .withColumn("total_amount", col("total_amount").cast(FloatType()))
    .dropDuplicates(["transaction_id"])
    .filter(col("quantity") > 0)
)

sales_silver.write.format("delta").mode("overwrite").saveAsTable("stihl_analytics.silver.sales")

# COMMAND ----------
# Transform inventory
inventory_bronze = spark.table("stihl_analytics.bronze.inventory_raw")

inventory_silver = (inventory_bronze
    .withColumn("snapshot_date", to_date(col("snapshot_date")))
    .withColumn("quantity_on_hand", col("quantity_on_hand").cast(IntegerType()))
    .withColumn("days_of_supply", col("days_of_supply").cast(FloatType()))
    .withColumn("status", when(col("days_of_supply") < 7, "CRITICAL")
                         .when(col("days_of_supply") < 14, "LOW")
                         .when(col("days_of_supply") > 90, "OVERSTOCK")
                         .otherwise("NORMAL"))
)

inventory_silver.write.format("delta").mode("overwrite").saveAsTable("stihl_analytics.silver.inventory")

# COMMAND ----------
# Transform products and dealers similarly...
```

### 4.4 04_vectorization.py

```python
# Databricks notebook source
# MAGIC %md
# MAGIC # Vectorization Layer
# MAGIC Generate narrative summaries and embeddings using External Model Endpoint

# COMMAND ----------
import mlflow.deployments

# Initialize embedding client
client = mlflow.deployments.get_deploy_client("databricks")

def get_embedding(text: str) -> list:
    """Get embedding from Azure OpenAI via External Model Endpoint"""
    response = client.predict(
        endpoint="azure-openai-embeddings",
        inputs={"input": text}
    )
    return response["data"][0]["embedding"]

# COMMAND ----------
from pyspark.sql.functions import udf, concat_ws
from pyspark.sql.types import ArrayType, FloatType

# Register UDF
embedding_udf = udf(get_embedding, ArrayType(FloatType()))

# COMMAND ----------
# Create sales narratives
sales = spark.table("stihl_analytics.silver.sales")
products = spark.table("stihl_analytics.silver.products")
dealers = spark.table("stihl_analytics.silver.dealers")

sales_enriched = (sales
    .join(products, "product_id")
    .join(dealers, "dealer_id")
)

sales_vectorized = sales_enriched.withColumn(
    "narrative",
    concat_ws(" ",
        lit("On"), col("transaction_date"),
        col("dealer_name"), lit("in"), col("region"),
        lit("sold"), col("quantity"), col("product_name"),
        lit("for $"), col("total_amount")
    )
).withColumn("embedding", embedding_udf(col("narrative")))

sales_vectorized.write.format("delta").mode("overwrite") \
    .saveAsTable("stihl_analytics.silver.sales_vectorized")
```

---

## 5. External Model Endpoint

Connect Databricks to Azure OpenAI for embeddings:

### 5.1 Create Endpoint

```python
import mlflow.deployments

client = mlflow.deployments.get_deploy_client("databricks")

# Create external model endpoint
client.create_endpoint(
    name="azure-openai-embeddings",
    config={
        "served_entities": [{
            "name": "text-embedding-ada-002",
            "external_model": {
                "name": "text-embedding-ada-002",
                "provider": "openai",
                "task": "llm/v1/embeddings",
                "openai_config": {
                    "openai_api_type": "azure",
                    "openai_api_key": "{{secrets/stihl-analytics/openai-key}}",
                    "openai_api_base": "https://openai-stihl-analytics.openai.azure.com/",
                    "openai_deployment_name": "text-embedding-ada-002",
                    "openai_api_version": "2024-02-01"
                }
            }
        }]
    }
)
```

### 5.2 Store Secret

```bash
# Using Databricks CLI
databricks secrets create-scope --scope stihl-analytics
databricks secrets put --scope stihl-analytics --key openai-key
```

---

## 6. Mosaic AI Vector Search

### 6.1 Create Vector Search Endpoint

```python
from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient()

# Create endpoint
vsc.create_endpoint(
    name="stihl-vector-endpoint",
    endpoint_type="STANDARD"
)
```

### 6.2 Create Vector Indexes

```python
# Products index (Silver)
vsc.create_delta_sync_index(
    endpoint_name="stihl-vector-endpoint",
    index_name="stihl_analytics.silver.products_vs_index",
    source_table_name="stihl_analytics.silver.products_vectorized",
    pipeline_type="TRIGGERED",
    primary_key="product_id",
    embedding_dimension=1536,
    embedding_vector_column="embedding"
)

# Sales monthly index (Gold)
vsc.create_delta_sync_index(
    endpoint_name="stihl-vector-endpoint",
    index_name="stihl_analytics.gold.sales_monthly_vs_index",
    source_table_name="stihl_analytics.gold.sales_monthly_vectorized",
    pipeline_type="TRIGGERED",
    primary_key="month_key",
    embedding_dimension=1536,
    embedding_vector_column="embedding"
)

# Insights index (Gold)
vsc.create_delta_sync_index(
    endpoint_name="stihl-vector-endpoint",
    index_name="stihl_analytics.gold.insights_vs_index",
    source_table_name="stihl_analytics.gold.insights_vectorized",
    pipeline_type="TRIGGERED",
    primary_key="insight_id",
    embedding_dimension=1536,
    embedding_vector_column="embedding"
)
```

### 6.3 Query Vector Index

```python
# Search for similar products
results = vsc.get_index(
    endpoint_name="stihl-vector-endpoint",
    index_name="stihl_analytics.silver.products_vs_index"
).similarity_search(
    query_text="professional chainsaw for large trees",
    columns=["product_id", "product_name", "msrp", "narrative"],
    num_results=5
)
```

---

## 7. Databricks Jobs

### 7.1 Daily Pipeline Job

```json
{
    "name": "stihl-daily-analytics-pipeline",
    "tasks": [
        {
            "task_key": "bronze_ingestion",
            "notebook_task": {
                "notebook_path": "/Workspace/stihl-analytics/01_bronze_ingestion"
            }
        },
        {
            "task_key": "silver_transform",
            "depends_on": [{"task_key": "bronze_ingestion"}],
            "notebook_task": {
                "notebook_path": "/Workspace/stihl-analytics/02_silver_transform"
            }
        },
        {
            "task_key": "gold_aggregation",
            "depends_on": [{"task_key": "silver_transform"}],
            "notebook_task": {
                "notebook_path": "/Workspace/stihl-analytics/03_gold_aggregation"
            }
        },
        {
            "task_key": "vectorization",
            "depends_on": [{"task_key": "gold_aggregation"}],
            "notebook_task": {
                "notebook_path": "/Workspace/stihl-analytics/04_vectorization"
            }
        },
        {
            "task_key": "anomaly_detection",
            "depends_on": [{"task_key": "vectorization"}],
            "notebook_task": {
                "notebook_path": "/Workspace/stihl-analytics/05_anomaly_detection"
            }
        },
        {
            "task_key": "forecasting",
            "depends_on": [{"task_key": "anomaly_detection"}],
            "notebook_task": {
                "notebook_path": "/Workspace/stihl-analytics/06_forecasting"
            }
        },
        {
            "task_key": "insight_generation",
            "depends_on": [{"task_key": "forecasting"}],
            "notebook_task": {
                "notebook_path": "/Workspace/stihl-analytics/07_insight_generation"
            }
        }
    ],
    "schedule": {
        "quartz_cron_expression": "0 0 6 * * ?",
        "timezone_id": "America/Los_Angeles"
    }
}
```

---

## 8. AI/BI Genie Space

For AI Foundry Databricks connector:

### 8.1 Create Genie Space

1. Navigate to **Data** → **AI/BI Genie**
2. Click **Create Genie Space**
3. Configure:
   - **Name**: `stihl-analytics-genie`
   - **Description**: Natural language access to STIHL data

### 8.2 Add Tables

Add these tables to Genie Space:
- `stihl_analytics.silver.sales`
- `stihl_analytics.silver.inventory`
- `stihl_analytics.silver.products`
- `stihl_analytics.gold.sales_monthly`
- `stihl_analytics.gold.dealer_performance`

### 8.3 Get Space ID

From URL: `https://adb-xxxxx.azuredatabricks.net/genie/spaces/<SPACE_ID>`

---

## ✅ Databricks Checklist

### Setup
- [ ] Databricks workspace accessible
- [ ] Unity Catalog enabled
- [ ] Catalog `stihl_analytics` created
- [ ] Schemas (bronze, silver, gold) created
- [ ] External storage location configured
- [ ] SQL Warehouse created

### ETL
- [ ] Bronze ingestion notebook working
- [ ] Silver transformation notebook working
- [ ] Gold aggregation notebook working
- [ ] Vectorization notebook working
- [ ] Anomaly detection notebook working
- [ ] Forecasting notebook working
- [ ] Insight generation notebook working

### Vector Search
- [ ] External Model Endpoint created
- [ ] Secret scope configured
- [ ] Vector Search Endpoint created
- [ ] Products index created
- [ ] Sales monthly index created
- [ ] Insights index created

### Integration
- [ ] Daily job scheduled
- [ ] Genie Space created
- [ ] Tables added to Genie Space
- [ ] PAT token generated for AI Foundry

---

## 🔗 Related Documents

- [INFRASTRUCTURE.md](../infrastructure/INFRASTRUCTURE.md) - Databricks workspace setup
- [DATA-LAYER.md](../data/DATA-LAYER.md) - Data schemas and medallion design
- [AGENT.md](../agent/AGENT.md) - How agent connects to Databricks

---

**Last Updated**: January 2026
