# Data Layer - Medallion Architecture & Synthetic Data

> **Parent**: [PROJECT-MASTER.md](../PROJECT-MASTER.md)  
> **Status**: ⏳ Pending  
> **Owner**: Data Engineering

---

## Overview

This document covers the data layer design including medallion architecture, synthetic data generation, and vectorization strategy.

**Storage**: ADLS Gen2 (`adlsstihlanalytics`)  
**Container**: `stihl-analytics-data`  
**Format**: Delta Lake (Silver/Gold), CSV/JSON (Bronze)

---

## 1. Medallion Architecture

```
ADLS Gen2: stihl-analytics-data/
│
├── BRONZE (Raw Files)
│   ├── sales_raw/*.csv
│   ├── inventory_raw/*.csv
│   ├── products_raw/products.json
│   └── dealers_raw/dealers.csv
│
├── SILVER (Delta Lake - Granular)
│   ├── sales/                    → Transaction-level
│   ├── inventory/                → Daily snapshots
│   ├── products/                 → Product catalog
│   ├── dealers/                  → Dealer info
│   ├── sales_vectorized/         → With embeddings
│   ├── inventory_vectorized/     → With embeddings
│   └── products_vectorized/      → With embeddings
│
└── GOLD (Delta Lake - Aggregated)
    ├── sales_monthly/            → Monthly rollups
    ├── inventory_monthly/        → Monthly snapshots
    ├── dealer_performance/       → Dealer metrics
    ├── sales_inv_combined/       → Joined view
    ├── detected_anomalies/       → Anomaly results
    ├── sales_forecasts/          → Prophet forecasts
    ├── proactive_insights/       → Pre-computed insights
    ├── sales_monthly_vectorized/ → With embeddings
    ├── insights_vectorized/      → With embeddings
    └── forecasts_vectorized/     → With embeddings
```

---

## 2. Data Volumes

| Dataset | Rows | Period | Size Est. |
|---------|------|--------|-----------|
| Products | ~200 | Static | < 1 MB |
| Sales | ~500,000 | Jan 2024 - Dec 2025 | ~100 MB |
| Inventory | ~150,000 | Daily × Products × Warehouses | ~50 MB |
| Dealers | ~100 | Static | < 1 MB |

---

## 3. Synthetic Data Schemas

### 3.1 Products

```python
products_schema = {
    "product_id": "str",        # e.g., "MS-271"
    "product_name": "str",      # e.g., "MS 271 Farm Boss"
    "category": "str",          # Chainsaw, Trimmer, Blower, etc.
    "subcategory": "str",       # Gas, Battery, Backpack, etc.
    "product_line": "str",      # Homeowner, Farm & Ranch, Professional
    "engine_cc": "float",       # e.g., 50.2
    "weight_lbs": "float",      # e.g., 12.3
    "msrp": "float",            # e.g., 449.99
    "cost": "float",            # e.g., 280.00
    "description": "str",       # Product description
    "features": "list[str]",    # Key features
    "power_type": "str",        # Gas, Battery, Electric
    "is_active": "bool"
}
```

### 3.2 Sales

```python
sales_schema = {
    "transaction_id": "str",    # UUID
    "transaction_date": "date",
    "product_id": "str",        # FK to products
    "dealer_id": "str",         # FK to dealers
    "quantity": "int",
    "unit_price": "float",
    "discount_pct": "float",
    "total_amount": "float",
    "customer_type": "str",     # Homeowner, Professional, Commercial
    "channel": "str",           # In-Store, Online, Phone
    "region": "str"             # Southwest, Southeast, etc.
}
```

### 3.3 Inventory

```python
inventory_schema = {
    "snapshot_date": "date",
    "product_id": "str",        # FK to products
    "warehouse_id": "str",      # e.g., "WH-TX-01"
    "region": "str",
    "quantity_on_hand": "int",
    "quantity_available": "int",
    "quantity_reserved": "int",
    "days_of_supply": "float",
    "reorder_point": "int",
    "status": "str"             # NORMAL, LOW, CRITICAL, OVERSTOCK
}
```

### 3.4 Dealers

```python
dealers_schema = {
    "dealer_id": "str",         # e.g., "DLR-AZ-001"
    "dealer_name": "str",
    "city": "str",
    "state": "str",
    "region": "str",
    "dealer_type": "str",       # Authorized, Premium, Service Center
    "year_established": "int",
    "is_active": "bool"
}
```

---

## 4. STIHL Product Categories

Based on official STIHL product lineup:

| Category | Count | Examples |
|----------|-------|----------|
| **Chainsaws** | ~50 | MS 170, 180, 250, 271, 291, 311, 362, 461, 500i, MSA battery |
| **Trimmers** | ~40 | FS 38, 40, 50, 56, 91, 111, 131, FSA battery |
| **Blowers** | ~30 | BG handheld, BR backpack, BGA battery |
| **Hedge Trimmers** | ~20 | HS gas, HSA battery, HL extended |
| **Lawn Mowers** | ~20 | RM gas, iMOW robotic |
| **Multi-System** | ~15 | KM series with attachments |
| **Accessories** | ~25 | Chains, bars, batteries, chargers, PPE |

---

## 5. Regional Distribution

| Region | % of Sales | Key States |
|--------|------------|------------|
| Southwest | 25% | TX, AZ, NM, OK |
| Southeast | 22% | FL, GA, NC, SC, AL |
| Midwest | 20% | OH, IN, IL, MI, WI |
| Northeast | 18% | NY, PA, NJ, MA, CT |
| West | 15% | CA, WA, OR, CO |

---

## 6. Seasonal Patterns

```python
seasonal_weights = {
    "January": 0.6,
    "February": 0.7,
    "March": 1.2,      # Spring start
    "April": 1.5,      # Peak
    "May": 1.5,        # Peak
    "June": 1.3,
    "July": 0.7,       # Summer slow
    "August": 0.7,     # Summer slow
    "September": 1.2,  # Fall start
    "October": 1.3,    # Peak
    "November": 1.4,   # Black Friday
    "December": 0.8
}
```

---

## 7. Injected Anomalies

For demo purposes, inject these anomalies:

| Anomaly | Type | Details |
|---------|------|---------|
| **Black Friday Spike** | Sales +300% | November 25-30, all categories |
| **Hurricane Texas** | Sales +340% | June, Chainsaws in TX |
| **Supply Disruption** | Sales -60% | August, Blowers nationwide |
| **Stockout** | Inventory 0 | MS-271 in Southwest, Q3 |
| **Overstock** | Inventory +200% | FS-91 in Northeast, Q4 |

---

## 8. Vectorization Strategy

### 8.1 Embedding Model

**Model**: Azure OpenAI `text-embedding-ada-002`  
**Delivery**: Databricks External Model Endpoint  
**Dimensions**: 1536

### 8.2 Silver Layer Narratives

**sales_vectorized** - Per transaction:
```
"On 2024-03-15, Arizona Power Equipment in Southwest sold 3 MS 271 Farm Boss 
chainsaws for $1,282.47 (unit price $449.99, 5% discount). Customer type: 
Professional. Channel: In-Store."
```

**inventory_vectorized** - Per snapshot:
```
"On 2024-03-15, WH-TX-01 (Southwest) had 145 units of MS 271 Farm Boss on hand 
(122 available, 23 reserved). Days of supply: 32.5. Status: NORMAL."
```

**products_vectorized** - Per product:
```
"MS 271 Farm Boss is a Gas Chainsaw in the Farm & Ranch line. It features 
50.2 cc power, weighs 12.3 lbs, and retails at $449.99. Professional-grade 
chainsaw ideal for cutting firewood, felling medium trees, and farm/ranch use."
```

### 8.3 Gold Layer Narratives

**sales_monthly_vectorized** - Monthly summary:
```
"In March 2024, Southwest region sold 2,340 units of Chainsaw products for 
$890,000 in revenue. This is +15% vs previous month and +8% vs same month 
last year. Top performing product: MS 271 Farm Boss."
```

**forecasts_vectorized** - Predictions:
```
"FORECAST: Chainsaw sales for Q1 2025 predicted at 45,000 units ($18.2M revenue), 
+12% vs Q1 2024. Confidence: 87%."
```

**insights_vectorized** - Anomalies/trends:
```
"ANOMALY DETECTED (HIGH): On 2024-06-15, chainsaw sales in Texas spiked 340% 
above normal (1,523 units vs 447 average). Correlation: Hurricane landfall. 
Affected dealers: 12."
```

---

## 9. Query Routing Matrix

| Question Type | Layer | Table | Method |
|---------------|-------|-------|--------|
| Product recommendations | Silver | products_vectorized | Vector Search |
| Specific transaction lookup | Silver | sales | SQL |
| Transaction search by criteria | Silver | sales_vectorized | Vector Search |
| Daily inventory status | Silver | inventory | SQL |
| Inventory issues search | Silver | inventory_vectorized | Vector Search |
| Monthly/quarterly summaries | Gold | sales_monthly | SQL |
| Period comparison questions | Gold | sales_monthly_vectorized | Vector Search |
| Anomaly/insight questions | Gold | insights_vectorized | Vector Search |
| Forecast questions | Gold | forecasts_vectorized | Vector Search |
| Proactive insights (on load) | Gold | proactive_insights | SQL |

---

## 10. Data Generation Scripts

Location: `data/synthetic/`

| Script | Purpose | Output |
|--------|---------|--------|
| `generate_products.py` | STIHL product catalog | `products.json` |
| `generate_dealers.py` | Dealer network | `dealers.csv` |
| `generate_sales.py` | 500K transactions | `sales_*.csv` |
| `generate_inventory.py` | Daily snapshots | `inventory_*.csv` |
| `inject_anomalies.py` | Add anomaly patterns | Updates sales/inventory |

---

## ✅ Data Layer Checklist

### Bronze
- [ ] Generate products.json (~200 products)
- [ ] Generate dealers.csv (~100 dealers)
- [ ] Generate sales CSVs (~500K rows)
- [ ] Generate inventory CSVs (~150K rows)
- [ ] Upload to ADLS bronze/

### Silver
- [ ] Create Delta tables from Bronze
- [ ] Add data quality checks
- [ ] Generate narrative columns
- [ ] Create vectorized tables
- [ ] Build Vector Search indexes

### Gold
- [ ] Create monthly aggregations
- [ ] Run anomaly detection
- [ ] Generate forecasts
- [ ] Create proactive insights
- [ ] Build Gold Vector Search indexes

---

## 🔗 Related Documents

- [INFRASTRUCTURE.md](../infrastructure/INFRASTRUCTURE.md) - ADLS Gen2 setup
- [DATABRICKS.md](../databricks/DATABRICKS.md) - ETL notebooks, Vector Search
- [AGENT.md](../agent/AGENT.md) - How agent queries data

---

**Last Updated**: January 2026
