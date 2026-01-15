# Databricks - Unity Catalog & ETL

> **Status: ✅ COMPLETE** (January 12, 2026)

---

## Workspace Details

| Setting | Value |
|---------|-------|
| Workspace Name | `dbw-stihl-analytics` |
| URL | https://adb-7405610757175308.8.azuredatabricks.net |
| SKU | Premium |
| Location | West US |
| Catalog | `dbw_stihl_analytics` |

---

## Unity Catalog Structure

```
dbw_stihl_analytics (catalog)
├── bronze (schema)
│   ├── products
│   ├── dealers
│   ├── sales
│   └── inventory
├── silver (schema)
│   ├── products
│   ├── dealers
│   ├── sales
│   └── inventory
├── gold (schema)
│   ├── monthly_sales
│   ├── product_performance
│   ├── dealer_performance
│   └── inventory_status
├── default (schema)
└── information_schema (schema)
```

---

## External Storage Configuration

### Storage Credential
| Setting | Value |
|---------|-------|
| Name | `stihl_adls_credential` |
| Type | Azure Managed Identity |
| Access Connector | `/subscriptions/f145b6d6-938e-4be9-876d-eac04dbda8e2/resourceGroups/rg-ai-foundry-learning/providers/Microsoft.Databricks/accessConnectors/dbw-stihl-access-connector` |

### External Location
| Setting | Value |
|---------|-------|
| Name | `stihl_adls_location` |
| URL | `abfss://stihl-analytics-data@adlsstihlanalytics.dfs.core.windows.net/` |
| Credential | `stihl_adls_credential` |
| Permissions | Read ✅, List ✅, Write ✅, Delete ✅ |

---

## Tables Overview

### Bronze Layer (Raw)

| Table | Records | Source |
|-------|---------|--------|
| `bronze.products` | 101 | products.json |
| `bronze.dealers` | 100 | dealers.csv |
| `bronze.sales` | 562,585 | sales_*.csv |
| `bronze.inventory` | 126,392 | inventory_*.csv |

### Silver Layer (Cleaned & Typed)

| Table | Records | Transformations |
|-------|---------|-----------------|
| `silver.products` | 101 | Type casting, null handling |
| `silver.dealers` | 100 | Type casting |
| `silver.sales` | 562,585 | Date parsing, numeric casting |
| `silver.inventory` | 126,392 | Date parsing, numeric casting |

### Gold Layer (Aggregated)

| Table | Records | Purpose |
|-------|---------|---------|
| `gold.monthly_sales` | ~1,680 | Monthly sales by category/region |
| `gold.product_performance` | 101 | Product sales rankings |
| `gold.dealer_performance` | 100 | Dealer sales rankings |
| `gold.inventory_status` | ~481 | Latest inventory snapshot |

---

## ETL Notebooks

### 01_bronze_ingestion.py
Loads raw data from ADLS into Bronze Delta tables.

```python
# Key operations
spark.read.option("multiLine", "true").json(adls_path + "/products_raw/products.json")
spark.read.option("header", "true").csv(adls_path + "/sales_raw/")
df.write.mode("overwrite").saveAsTable("products")
```

### 02_silver_transform.py
Cleans and type-casts Bronze data to Silver.

```python
# Key transformations
col("msrp").cast("double")
to_date(col("transaction_date"))
col("quantity").cast("int")
```

### 03_gold_aggregation.py
Creates analytics-ready aggregated tables.

```python
# Key aggregations
sales.groupBy(year, month, category, region)
    .agg(sum("total_amount"), count("*"))
```

---

## Sample Queries

### Monthly Sales by Category
```sql
SELECT year, month, category, 
       SUM(total_revenue) as revenue
FROM dbw_stihl_analytics.gold.monthly_sales
GROUP BY year, month, category
ORDER BY year, month;
```

### Top Products by Revenue
```sql
SELECT product_name, category, total_revenue
FROM dbw_stihl_analytics.gold.product_performance
ORDER BY total_revenue DESC
LIMIT 10;
```

### Inventory Alerts
```sql
SELECT product_name, warehouse_id, region, 
       quantity_on_hand, days_of_supply, status
FROM dbw_stihl_analytics.gold.inventory_status
WHERE status IN ('CRITICAL', 'OUT_OF_STOCK')
ORDER BY days_of_supply;
```

### Hurricane Texas Analysis
```sql
SELECT DATE_TRUNC('day', transaction_date) as date,
       COUNT(*) as transactions,
       SUM(total_amount) as revenue
FROM dbw_stihl_analytics.silver.sales
WHERE state = 'TX' 
  AND category = 'Chainsaws'
  AND transaction_date BETWEEN '2024-06-01' AND '2024-06-30'
GROUP BY 1
ORDER BY 1;
```

---

## Compute Resources

### SQL Warehouse (Serverless)
- Type: Serverless Starter Warehouse
- Auto-stop: 10 minutes
- Used for: SQL Editor queries, Genie

### Serverless Compute
- Used for: Notebook execution
- Auto-scales based on workload

---

## Setup Commands (SQL)

### Create Schemas
```sql
USE CATALOG dbw_stihl_analytics;
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;
```

### Create Storage Credential (via UI)
1. Catalog → External Data → Credentials
2. Create credential with Access Connector ID

### Create External Location (via UI)
1. Catalog → External Data → External Locations
2. Create location with credential and URL

---

## ✅ Checklist (Completed)

- [x] Access Databricks workspace
- [x] Verify Unity Catalog enabled
- [x] Create bronze/silver/gold schemas
- [x] Create Access Connector (managed identity)
- [x] Assign Storage Blob Data Contributor role
- [x] Create storage credential
- [x] Create external location
- [x] Test connection (all permissions confirmed)
- [x] Run 01_bronze_ingestion notebook
- [x] Run 02_silver_transform notebook
- [x] Run 03_gold_aggregation notebook
- [x] Verify all 12 tables created

---

## Next Steps (Phase 4)

- [ ] Create Genie Space for AI/BI queries
- [ ] Set up Vector Search endpoint
- [ ] Connect AI Foundry agent to Databricks
- [ ] Test natural language queries

---

## Related Documents

- [PROJECT-MASTER.md](../PROJECT-MASTER.md) - Main project hub
- [INFRASTRUCTURE.md](../infrastructure/INFRASTRUCTURE.md) - Azure resources
- [DATA-LAYER.md](../data/DATA-LAYER.md) - Data architecture
- [AGENT.md](../agent/AGENT.md) - AI agent (next phase)

---

*Last Updated: January 12, 2026*
