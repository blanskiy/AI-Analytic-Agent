# STIHL Analytics Agent - Project Summary

## Project Overview
Building an AI-powered analytics agent for STIHL power equipment data that demonstrates advanced Azure AI capabilities including proactive insights, natural language querying, anomaly detection, and RAG-based semantic search.

**Repository:** https://github.com/blanskiy/AI-Analytic-Agent
**Latest Commit:** Phase 5b complete - RAG with Databricks Vector Search

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
│  Agent routes query to appropriate tool:                        │
│  ├── SQL Tools (quantitative) → Databricks SQL Warehouse        │
│  └── RAG Tools (qualitative) → Databricks Vector Search         │
│      ↓                                                           │
│  Results returned → Natural language response                   │
└─────────────────────────────────────────────────────────────────┘
```

### Tool Routing Logic
```
┌─────────────────────────────────────────────────────────────────┐
│  Query Type              │  Tool                    │  Backend  │
├──────────────────────────┼──────────────────────────┼───────────┤
│  Revenue, metrics        │  query_sales_data        │  SQL      │
│  Stock levels            │  query_inventory_data    │  SQL      │
│  Alerts, anomalies       │  get_proactive_insights  │  SQL      │
│  Product features        │  search_products         │  Vector   │
│  Recommendations         │  get_product_recommendations│ Vector │
│  Compare products        │  compare_products        │  SQL+Vec  │
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
| Vector Endpoint | stihl-vector-endpoint | STANDARD tier |
| Vector Index | product_index | BGE-Large embeddings |

---

## Databricks Schema Structure

### Catalog: `dbw_stihl_analytics`

#### Silver Schema (Cleansed Data)
All tables partitioned by year, month.

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

**silver.products** (101 products)
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
description STRING  ← Used for RAG embeddings
features ARRAY<STRING>  ← Used for RAG embeddings
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
**gold.inventory_status**
**gold.product_performance**
**gold.dealer_performance**
**gold.proactive_insights** (13 critical anomalies)

#### Vectors Schema (Phase 5b - NEW)

**vectors.product_embeddings_source** (101 rows)
```
product_id STRING (primary key)
product_name STRING
category STRING
subcategory STRING
power_type STRING
weight_lbs DOUBLE
msrp DOUBLE
description STRING
features_text STRING
embedding_text STRING  ← Concatenated text for embedding generation
```
- Change Data Feed enabled for Delta Sync
- Synced to Vector Search index

**Vector Search Resources:**
- **Endpoint:** stihl-vector-endpoint (STANDARD)
- **Index:** dbw_stihl_analytics.vectors.product_index
- **Embedding Model:** databricks-bge-large-en
- **Pipeline Type:** TRIGGERED (manual sync)

---

## Agent Implementation

### Local Project Structure
```
C:\Users\blans\source\repos\ai-analytic-agent\
├── agent/
│   ├── __init__.py
│   ├── agent_realtime.py      ← Main orchestrator with Azure OpenAI function calling
│   ├── databricks_client.py   ← SQL warehouse connection
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── system_prompt.py   ← Updated with RAG routing logic
│   └── tools/
│       ├── __init__.py        ← Exports TOOL_FUNCTIONS, TOOL_DEFINITIONS (8 tools)
│       ├── sales_tools.py     ← query_sales_data
│       ├── inventory_tools.py ← query_inventory_data
│       ├── insights_tools.py  ← get_proactive_insights, detect_anomalies_realtime, get_daily_briefing
│       └── rag_tools.py       ← search_products, compare_products, get_product_recommendations (NEW)
├── config/
│   ├── __init__.py
│   └── settings.py
├── databricks/
│   └── notebooks/
│       ├── proactive_insights_pipeline.py
│       └── setup_vector_search.py  (NEW)
├── tests/
│   ├── __init__.py
│   ├── test_databricks_connection.py
│   ├── test_tools.py
│   └── test_rag_tools.py      (NEW)
├── .env
└── requirements.txt
```

### Agent Tools (8 Total)

| Tool | Type | Function | Use Case |
|------|------|----------|----------|
| `query_sales_data` | SQL | Revenue, trends, product performance | "What's our total revenue?" |
| `query_inventory_data` | SQL | Stock levels, stockouts | "Products running low?" |
| `get_proactive_insights` | SQL | Pre-computed anomalies, alerts | "Any critical issues?" |
| `detect_anomalies_realtime` | SQL | Z-score analysis on any period | "Anomalies in March 2024" |
| `get_daily_briefing` | SQL | Combined metrics + insights | "Good morning!" |
| `search_products` | RAG | Semantic product search | "Best chainsaw for professionals" |
| `compare_products` | SQL | Side-by-side comparison | "Compare MS 500i vs MS 462" |
| `get_product_recommendations` | RAG | Use case-based recommendations | "What do I need for 5 acres?" |

### Agent Capabilities Verified

```
✅ SQL Queries:
   "What were our top selling products?" → query_sales_data
   "How is the Southwest region doing?" → query_sales_data + query_inventory_data
   "Run anomaly detection for March 2024" → detect_anomalies_realtime

✅ RAG Queries (NEW):
   "What chainsaw is best for professional logging?" → search_products
   "Recommend a lightweight battery trimmer under $300" → search_products with filters
   "Compare the MS 500i and MS 462" → compare_products
   "What products have anti-vibration features?" → search_products
   "I have 5 acres, what do I need?" → get_product_recommendations
```

### Running the Agent

```powershell
cd C:\Users\blans\source\repos\ai-analytic-agent
.venv\Scripts\activate
python -m agent.agent_realtime

# Run all tests
python -m tests.test_tools
python -m tests.test_rag_tools
```

---

## Key Data Points

| Metric | Value |
|--------|-------|
| Total Revenue | $394,927,843 |
| Total Units | 816,913 |
| Time Range | Jan 2024 - Dec 2025 (24 months) |
| Products | 101 active |
| Categories | 7 |
| Top Region | Southwest ($99.3M) |
| Top Product | MS 881 ($21.4M) |

### Product Data Quality (RAG)
| Metric | Count |
|--------|-------|
| Total products | 101 |
| Active products | 101 (100%) |
| Has description | 101 (100%) |
| Has features | 77 (76%) |
| Categories | 7 |

### Injected Demo Anomalies
- **March 2024**: Sales spike across all categories (+80-122% above expected)
- **June 2024 Southwest**: Hurricane TX event (Chainsaws $2.2M spike)

---

## Environment Variables (.env)

```bash
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

# Azure OpenAI
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

### Phase 5a: Table Partitioning ✅
- silver.sales partitioned by year, month
- silver.inventory partitioned by year, month  
- gold.monthly_sales partitioned by year, month
- ZORDER optimization applied
- Backup tables preserved in default schema

### Phase 5b: RAG with Vector Search ✅ (COMPLETE)
- Created `vectors` schema in Unity Catalog
- Built `product_embeddings_source` table with enriched text
- Deployed Vector Search endpoint (stihl-vector-endpoint)
- Created HNSW index with BGE-Large embeddings
- Implemented 3 RAG tools: search_products, compare_products, get_product_recommendations
- Updated agent tool registry and system prompt
- All RAG tests passing

---

## Next Steps: Phase 6 - UI Implementation

### Planned Approach
1. **Phase 6a**: Test in Azure AI Foundry Playground
2. **Phase 6b**: Custom React UI with Plotly visualizations

### Potential Features
- Chat interface with tool call visibility
- Interactive charts for sales/inventory data
- Product comparison cards
- Anomaly visualization timeline

---

## Files to Reference

| File | Purpose |
|------|---------|
| `agent/agent_realtime.py` | Main orchestrator - start here |
| `agent/tools/rag_tools.py` | RAG implementation (NEW) |
| `agent/tools/insights_tools.py` | Anomaly detection logic |
| `agent/prompts/system_prompt.py` | Tool routing logic |
| `agent/databricks_client.py` | SQL connection |
| `config/settings.py` | Environment variable handling |
| `tests/test_rag_tools.py` | RAG tool tests (NEW) |

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
python -m tests.test_rag_tools

# Git operations
git add .
git commit -m "Phase 5b: RAG with Databricks Vector Search"
git push origin main
```

---

## Databricks Notebooks Reference

### Setup Vector Search (databricks/notebooks/setup_vector_search.py)
```python
# Install SDK (run once per cluster)
# %%sh
# uv pip install databricks-vectorsearch --system

from databricks.vector_search.client import VectorSearchClient

vsc = VectorSearchClient(disable_notice=True)

# Create endpoint
vsc.create_endpoint(name="stihl-vector-endpoint", endpoint_type="STANDARD")

# Create index
vsc.create_delta_sync_index(
    endpoint_name="stihl-vector-endpoint",
    index_name="dbw_stihl_analytics.vectors.product_index",
    source_table_name="dbw_stihl_analytics.vectors.product_embeddings_source",
    primary_key="product_id",
    embedding_source_column="embedding_text",
    embedding_model_endpoint_name="databricks-bge-large-en",
    pipeline_type="TRIGGERED"
)

# Test search
index = vsc.get_index("stihl-vector-endpoint", "dbw_stihl_analytics.vectors.product_index")
results = index.similarity_search(
    query_text="professional chainsaw",
    columns=["product_id", "product_name", "description"],
    num_results=5
)
```

---

## Known Issues / Notes

1. **Status case sensitivity**: Inventory status values are UPPERCASE (CRITICAL, LOW, NORMAL)
2. **Anomaly detection**: Requires minimum 2 months historical data
3. **Vector Search endpoint**: Costs ~$0.07/hour when running - stop when not in use
4. **Change Data Feed**: Required on source table for Delta Sync indexes
5. **SDK installation**: Use `uv pip install databricks-vectorsearch --system` in notebooks
6. **Weight/price filters**: Applied as post-filters in code (Vector Search only supports categorical filters)

---

*Last Updated: January 14, 2025*
*Phase 5b Complete - RAG with Databricks Vector Search*
