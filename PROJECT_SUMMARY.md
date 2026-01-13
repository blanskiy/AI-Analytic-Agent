# STIHL Analytics Agent - Project Summary

## Project Overview
Building an AI-powered analytics agent for STIHL power equipment data that demonstrates advanced Azure AI capabilities including proactive insights, natural language querying, anomaly detection, and (next) RAG-based semantic search.

**Repository:** https://github.com/blanskiy/AI-Analytic-Agent
**Latest Commit:** Phase 4 complete with live function calling

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STIHL ANALYTICS AGENT                        │
├─────────────────────────────────────────────────────────────────┤
│  User Query                                                      │
│      ↓                                                           │
│  Azure OpenAI (gpt-4o-mini) with Function Calling               │
│      ↓                                                           │
│  Agent selects tool → Executes Python function                  │
│      ↓                                                           │
│  Databricks SQL Warehouse (live queries)                        │
│      ↓                                                           │
│  Results returned → Natural language response                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Azure Resources

| Resource | Name | Details |
|----------|------|---------|
| Resource Group | rg-ai-foundry-learning | West US |
| Azure OpenAI | (in AI Foundry) | gpt-4o-mini deployment |
| AI Foundry Project | stihl-analytics-agent | |
| Databricks Workspace | dbw-stihl-analytics | adb-7405610757175308.8.azuredatabricks.net |
| SQL Warehouse | ef25929815cf2952 | Serverless |
| Unity Catalog | dbw_stihl_analytics | |

---

## Databricks Schema Structure

### Catalog: `dbw_stihl_analytics`

#### Silver Schema (Cleansed Data)
All tables now **partitioned by year, month**.

**silver.sales** (562,585 rows)
```
transaction_id STRING
transaction_date DATE
product_id STRING
product_name STRING
category STRING
dealer_id STRING
dealer_name STRING
region STRING
state STRING
quantity INT
unit_price DOUBLE
discount_pct DOUBLE
total_amount DOUBLE
customer_type STRING
channel STRING
year INT (partition)
month INT (partition)
```

**silver.inventory** (126,392 rows)
```
snapshot_date DATE
product_id STRING
product_name STRING
category STRING
warehouse_id STRING
region STRING
quantity_on_hand INT
quantity_available INT
quantity_reserved INT
reorder_point INT
days_of_supply DOUBLE
status STRING (CRITICAL, LOW, NORMAL)
year INT (partition)
month INT (partition)
```

**silver.products** (~37 products)
```
product_id STRING
product_name STRING
category STRING
subcategory STRING
product_line STRING
power_type STRING (Gas, Battery, Electric)
engine_cc DOUBLE
voltage INT
weight_lbs DOUBLE
msrp DOUBLE
cost DOUBLE
description STRING  ← Has content, good for RAG
features ARRAY<STRING>  ← Has content, good for RAG
is_active BOOLEAN
```

**silver.dealers** 
```
dealer_id STRING
dealer_name STRING
city STRING
state STRING
region STRING
dealer_type STRING
year_established INT
is_active BOOLEAN
```

#### Gold Schema (Aggregated)

**gold.monthly_sales** (partitioned by year, month)
```
year INT (partition)
month INT (partition)
category STRING
region STRING
transaction_count BIGINT
total_units BIGINT
total_revenue DOUBLE
avg_transaction_value DOUBLE
```

**gold.inventory_status**
```
product_id STRING
product_name STRING
category STRING
warehouse_id STRING
region STRING
quantity_on_hand INT
quantity_available INT
days_of_supply DOUBLE
status STRING
```

**gold.product_performance**
```
product_id STRING
product_name STRING
category STRING
transaction_count BIGINT
total_units_sold BIGINT
total_revenue DOUBLE
avg_discount_pct DOUBLE
```

**gold.dealer_performance**
```
dealer_id STRING
dealer_name STRING
region STRING
state STRING
transaction_count BIGINT
total_units_sold BIGINT
total_revenue DOUBLE
```

**gold.proactive_insights** (13 critical anomalies)
```
insight_id STRING
insight_type STRING
severity STRING
title STRING
description STRING
affected_entity STRING
affected_entity_type STRING
metric_name STRING
metric_value DOUBLE
expected_value DOUBLE
deviation_pct DOUBLE
detected_at TIMESTAMP
is_active BOOLEAN
recommended_action STRING
supporting_data STRING
```

#### Backup Tables (in default schema)
- default.sales_backup
- default.inventory_backup
- default.monthly_sales_backup

---

## Agent Implementation (Phase 4 - Complete)

### Local Project Structure
```
C:\Users\blans\source\repos\ai-analytic-agent\
├── agent/
│   ├── __init__.py
│   ├── agent_realtime.py      ← Main orchestrator with Azure OpenAI function calling
│   ├── databricks_client.py   ← SQL warehouse connection
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── system_prompt.py
│   └── tools/
│       ├── __init__.py        ← Exports TOOL_FUNCTIONS, TOOL_DEFINITIONS
│       ├── sales_tools.py     ← query_sales_data (6 query types)
│       ├── inventory_tools.py ← query_inventory_data (7 query types)
│       └── insights_tools.py  ← get_proactive_insights, detect_anomalies_realtime, get_daily_briefing
├── config/
│   ├── __init__.py
│   └── settings.py            ← Reads from .env, supports multiple variable names
├── databricks/
│   └── notebooks/
│       └── proactive_insights_pipeline.py
├── tests/
│   ├── __init__.py
│   ├── test_databricks_connection.py
│   └── test_tools.py
├── .env                       ← Contains all credentials
└── requirements.txt
```

### Working Agent Tools

| Tool | Function | Use Case |
|------|----------|----------|
| `query_sales_data` | SQL queries on gold.monthly_sales, gold.product_performance | Revenue, trends, top products, regional analysis |
| `query_inventory_data` | SQL queries on gold.inventory_status | Stock levels, stockouts, days of supply |
| `get_proactive_insights` | Reads gold.proactive_insights or generates real-time | Anomalies, alerts at conversation start |
| `detect_anomalies_realtime` | Z-score analysis on any month | Specific period anomaly detection |
| `get_daily_briefing` | Combines metrics + top insights | Daily overview |

### Agent Capabilities Verified

```
✅ "Good morning! What should I know today?" → Calls get_daily_briefing + get_proactive_insights
✅ "What were our top selling products?" → Calls query_sales_data
✅ "How is the Southwest region doing?" → Calls BOTH query_sales_data AND query_inventory_data
✅ "Run anomaly detection on revenue by category for March 2024" → Calls detect_anomalies_realtime with time_period
✅ "Show me sales trends over time" → Returns 24 months of data with insights
```

### Running the Agent

```powershell
cd C:\Users\blans\source\repos\ai-analytic-agent
.venv\Scripts\activate
python -m agent.agent_realtime
```

---

## Key Data Points

| Metric | Value |
|--------|-------|
| Total Revenue | $394,927,843 |
| Total Units | 816,913 |
| Time Range | Jan 2024 - Dec 2025 (24 months) |
| Top Region | Southwest ($99.3M) |
| Top Product | MS 881 ($21.4M) |

### Injected Demo Anomalies
- **March 2024**: Sales spike across all categories (+80-122% above expected)
- **June 2024 Southwest**: Hurricane TX event (Chainsaws $2.2M spike)

---

## Environment Variables (.env)

```
# Databricks
DATABRICKS_HOST=adb-7405610757175308.8.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/ef25929815cf2952
DATABRICKS_TOKEN=<your-databricks-token>
DATABRICKS_CATALOG=dbw_stihl_analytics
DATABRICKS_SCHEMA_BRONZE=bronze
DATABRICKS_SCHEMA_SILVER=silver
DATABRICKS_SCHEMA_GOLD=gold

# Azure AI Foundry
AZURE_SUBSCRIPTION_ID=f145b6d6-938e-4be9-876d-eac04dbda8e2
AZURE_AI_PROJECT_NAME=stihl-analytics-agent
AZURE_RESOURCE_GROUP=rg-ai-foundry-learning
AZURE_LOCATION=westus

# Azure OpenAI (need to verify these are in .env)
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT_GPT=gpt-4o-mini
```

---

## Completed Phases

### Phase 1-3: Infrastructure & Data ✅
- Azure resources provisioned
- Databricks workspace with Unity Catalog
- Medallion architecture (bronze/silver/gold)
- ETL pipelines executed
- Demo anomalies injected

### Phase 4: AI Agent with Live Function Calling ✅
- 5 working tools connected to Databricks
- Azure OpenAI function calling orchestrator
- Real-time queries against live data
- Anomaly detection with time_period parameter
- All tests passing

### Phase 5a: Table Partitioning ✅ (Just Completed)
- silver.sales partitioned by year, month
- silver.inventory partitioned by year, month  
- gold.monthly_sales partitioned by year, month
- ZORDER optimization applied
- Backup tables preserved in default schema

---

## Next Steps: Phase 5b - RAG Implementation

### Goal
Add semantic search capability so agent can answer qualitative questions about products based on description and features.

### RAG Scope
- **Products**: Has `description` (string) and `features` (array<string>) - VIABLE for RAG
- **Dealers**: Only categorical fields - NOT viable for RAG
- **Sales/Inventory**: Numerical data - Use SQL, not RAG

### Implementation Plan

#### Step 1: Create Vectors Schema and Source Table
```sql
CREATE SCHEMA IF NOT EXISTS dbw_stihl_analytics.vectors;

CREATE TABLE dbw_stihl_analytics.vectors.product_embeddings_source (
    product_id STRING,
    product_name STRING,
    category STRING,
    subcategory STRING,
    power_type STRING,
    weight_lbs DOUBLE,
    msrp DOUBLE,
    description STRING,
    features_text STRING,
    embedding_text STRING
) USING DELTA;

INSERT OVERWRITE dbw_stihl_analytics.vectors.product_embeddings_source
SELECT 
    product_id,
    product_name,
    category,
    subcategory,
    power_type,
    weight_lbs,
    msrp,
    description,
    CONCAT_WS(', ', features) as features_text,
    CONCAT_WS(' | ', 
        product_name,
        category,
        COALESCE(subcategory, ''),
        COALESCE(power_type, ''),
        CONCAT('Weight: ', weight_lbs, ' lbs'),
        COALESCE(description, ''),
        CONCAT_WS(', ', features)
    ) as embedding_text
FROM dbw_stihl_analytics.silver.products
WHERE is_active = true;
```

#### Step 2: Create Vector Search Endpoint (Python notebook)
```python
from databricks.vector_search.client import VectorSearchClient
vsc = VectorSearchClient()
vsc.create_endpoint(name="stihl-vector-endpoint", endpoint_type="STANDARD")
```

#### Step 3: Create HNSW Index
```python
vsc.create_delta_sync_index(
    endpoint_name="stihl-vector-endpoint",
    index_name="dbw_stihl_analytics.vectors.product_index",
    source_table_name="dbw_stihl_analytics.vectors.product_embeddings_source",
    primary_key="product_id",
    embedding_source_column="embedding_text",
    embedding_model_endpoint_name="databricks-bge-large-en",
    pipeline_type="TRIGGERED"
)
```

#### Step 4: Create RAG Tool (agent/tools/rag_tools.py)
- `search_products(query, category, power_type, max_weight, max_price, top_k)`
- Uses Databricks Vector Search for similarity matching

#### Step 5: Update Agent
- Add `search_products` to TOOL_FUNCTIONS and TOOL_DEFINITIONS
- Update system prompt with routing logic:
  - Numbers/metrics → SQL tools
  - Features/recommendations → RAG tool

### Expected RAG Queries After Implementation
```
"What chainsaw is best for professionals?" → search_products (RAG)
"Lightweight battery trimmer options" → search_products (RAG)
"Which products have Easy2Start?" → search_products (RAG)
"Compare MS 500i vs MS 462 features" → search_products (RAG)
```

---

## Files to Reference

| File | Purpose |
|------|---------|
| `agent/agent_realtime.py` | Main orchestrator - start here |
| `agent/tools/insights_tools.py` | Most complex tool with anomaly detection |
| `agent/databricks_client.py` | SQL connection logic |
| `config/settings.py` | Environment variable handling |
| `tests/test_tools.py` | Comprehensive tool testing |

---

## Commands Reference

```powershell
# Activate environment
cd C:\Users\blans\source\repos\ai-analytic-agent
.venv\Scripts\activate

# Run agent
python -m agent.agent_realtime

# Run tests
python -m tests.test_tools

# Git commit
git add .
git commit -m "message"
git push origin main
```

---

## Known Issues / Notes

1. **Status case sensitivity**: Inventory status values are UPPERCASE (CRITICAL, LOW, NORMAL)
2. **Anomaly detection**: Requires minimum 2 months historical data
3. **Backup tables**: Original unpartitioned tables in default schema as *_backup
4. **Products table**: Has description and features - ready for RAG
5. **Dealers table**: No text fields for semantic search - SQL only

---

*Last Updated: January 13, 2026*
*Phase 4 Complete, Phase 5b (RAG) Next*
