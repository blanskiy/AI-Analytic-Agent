# Databricks notebook source
# MAGIC %md
# MAGIC # Setup Vector Search for STIHL Analytics Agent
# MAGIC 
# MAGIC This notebook sets up Databricks Vector Search infrastructure for RAG capabilities.
# MAGIC 
# MAGIC **Prerequisites:**
# MAGIC - Unity Catalog enabled workspace
# MAGIC - Premium tier (Vector Search feature)
# MAGIC - `dbw_stihl_analytics` catalog exists with `silver.products` populated
# MAGIC 
# MAGIC **Created:** Phase 5b - RAG Implementation

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Install Vector Search SDK

# COMMAND ----------

# MAGIC %%sh
# MAGIC uv pip install databricks-vectorsearch --system

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Create Vectors Schema and Source Table
# MAGIC 
# MAGIC Run this in SQL Editor or uncomment below:

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Create vectors schema
# MAGIC CREATE SCHEMA IF NOT EXISTS dbw_stihl_analytics.vectors
# MAGIC COMMENT 'Schema for vector embeddings and RAG components';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Create and populate source table for embeddings
# MAGIC CREATE OR REPLACE TABLE dbw_stihl_analytics.vectors.product_embeddings_source (
# MAGIC     product_id STRING NOT NULL,
# MAGIC     product_name STRING,
# MAGIC     category STRING,
# MAGIC     subcategory STRING,
# MAGIC     power_type STRING,
# MAGIC     weight_lbs DOUBLE,
# MAGIC     msrp DOUBLE,
# MAGIC     description STRING,
# MAGIC     features_text STRING,
# MAGIC     embedding_text STRING COMMENT 'Concatenated text for embedding generation'
# MAGIC ) USING DELTA
# MAGIC COMMENT 'Source table for product vector embeddings';
# MAGIC 
# MAGIC INSERT OVERWRITE dbw_stihl_analytics.vectors.product_embeddings_source
# MAGIC SELECT 
# MAGIC     product_id,
# MAGIC     product_name,
# MAGIC     category,
# MAGIC     subcategory,
# MAGIC     power_type,
# MAGIC     weight_lbs,
# MAGIC     msrp,
# MAGIC     description,
# MAGIC     CONCAT_WS(', ', features) as features_text,
# MAGIC     CONCAT_WS(' | ', 
# MAGIC         CONCAT('Product: ', product_name),
# MAGIC         CONCAT('Category: ', category),
# MAGIC         CONCAT('Type: ', COALESCE(subcategory, 'General')),
# MAGIC         CONCAT('Power: ', COALESCE(power_type, 'Not specified')),
# MAGIC         CONCAT('Weight: ', CAST(weight_lbs AS STRING), ' lbs'),
# MAGIC         CONCAT('Price: $', CAST(CAST(msrp AS INT) AS STRING)),
# MAGIC         CONCAT('Description: ', COALESCE(description, '')),
# MAGIC         CONCAT('Features: ', COALESCE(CONCAT_WS(', ', features), ''))
# MAGIC     ) as embedding_text
# MAGIC FROM dbw_stihl_analytics.silver.products
# MAGIC WHERE is_active = true;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Enable Change Data Feed (required for Delta Sync)
# MAGIC ALTER TABLE dbw_stihl_analytics.vectors.product_embeddings_source
# MAGIC SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Verify source table
# MAGIC SELECT 
# MAGIC     product_id, 
# MAGIC     product_name, 
# MAGIC     category,
# MAGIC     LEFT(embedding_text, 150) as embedding_preview
# MAGIC FROM dbw_stihl_analytics.vectors.product_embeddings_source
# MAGIC LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Create Vector Search Endpoint

# COMMAND ----------

from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient(disable_notice=True)

ENDPOINT_NAME = "stihl-vector-endpoint"

# Check if endpoint exists, create if not
try:
    endpoint = vsc.get_endpoint(ENDPOINT_NAME)
    state = endpoint.get('endpoint_status', {}).get('state')
    print(f"✅ Endpoint '{ENDPOINT_NAME}' already exists. State: {state}")
except Exception as e:
    print(f"Creating endpoint '{ENDPOINT_NAME}'...")
    vsc.create_endpoint(
        name=ENDPOINT_NAME,
        endpoint_type="STANDARD"
    )
    print(f"⏳ Endpoint creation initiated. This takes 5-10 minutes.")

# COMMAND ----------

# Check endpoint status (run until ONLINE)
endpoint = vsc.get_endpoint(ENDPOINT_NAME)
state = endpoint.get('endpoint_status', {}).get('state')
print(f"Endpoint state: {state}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Create Vector Search Index
# MAGIC 
# MAGIC **Wait for endpoint to be ONLINE before running this cell.**

# COMMAND ----------

ENDPOINT_NAME = "stihl-vector-endpoint"
INDEX_NAME = "dbw_stihl_analytics.vectors.product_index"
SOURCE_TABLE = "dbw_stihl_analytics.vectors.product_embeddings_source"

try:
    index = vsc.get_index(ENDPOINT_NAME, INDEX_NAME)
    print(f"✅ Index '{INDEX_NAME}' already exists.")
    print(f"   Status: {index.describe().get('status')}")
except Exception as e:
    print(f"Creating index '{INDEX_NAME}'...")
    
    vsc.create_delta_sync_index(
        endpoint_name=ENDPOINT_NAME,
        index_name=INDEX_NAME,
        source_table_name=SOURCE_TABLE,
        primary_key="product_id",
        embedding_source_column="embedding_text",
        embedding_model_endpoint_name="databricks-bge-large-en",
        pipeline_type="TRIGGERED"
    )
    print(f"⏳ Index creation initiated. This takes 3-5 minutes.")

# COMMAND ----------

# Check index status (run until ready: True)
index = vsc.get_index(ENDPOINT_NAME, INDEX_NAME)
status = index.describe()
print(f"Index: {INDEX_NAME}")
print(f"Status: {status.get('status')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Test Vector Search

# COMMAND ----------

# Test similarity search
index = vsc.get_index("stihl-vector-endpoint", "dbw_stihl_analytics.vectors.product_index")

results = index.similarity_search(
    query_text="professional chainsaw for heavy logging",
    columns=["product_id", "product_name", "category", "power_type", "description"],
    num_results=5
)

print("🔍 Search: 'professional chainsaw for heavy logging'\n")
for row in results.get('result', {}).get('data_array', []):
    print(f"  {row[1]} ({row[0]})")
    print(f"    Category: {row[2]} | Power: {row[3]}")
    print(f"    {row[4][:80]}...")
    print()

# COMMAND ----------

# Test with filters
test_queries = [
    ("lightweight battery trimmer for homeowner", None, None),
    ("quiet blower for residential use", "Blowers", None),
    ("professional chainsaw", "Chainsaws", "Gas"),
]

for query, category, power_type in test_queries:
    filters = {}
    if category:
        filters["category"] = category
    if power_type:
        filters["power_type"] = power_type
    
    results = index.similarity_search(
        query_text=query,
        columns=["product_id", "product_name", "category", "power_type", "msrp"],
        filters=filters if filters else None,
        num_results=3
    )
    
    print(f"🔍 '{query}'")
    if filters:
        print(f"   Filters: {filters}")
    for row in results.get('result', {}).get('data_array', []):
        print(f"   {row[1]} | {row[2]} | {row[3]} | ${row[4]}")
    print()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Maintenance Commands

# COMMAND ----------

# Sync index (run after source table updates)
# index.sync()

# COMMAND ----------

# Stop endpoint to save costs (when not in use)
# vsc.delete_endpoint(ENDPOINT_NAME)  # WARNING: This deletes the endpoint

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC **Created Resources:**
# MAGIC - Schema: `dbw_stihl_analytics.vectors`
# MAGIC - Table: `dbw_stihl_analytics.vectors.product_embeddings_source` (101 rows)
# MAGIC - Endpoint: `stihl-vector-endpoint` (STANDARD)
# MAGIC - Index: `dbw_stihl_analytics.vectors.product_index` (BGE-Large embeddings)
# MAGIC 
# MAGIC **Cost:** ~$0.07/hour for STANDARD endpoint when running
