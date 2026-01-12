# Data Layer - Medallion Architecture

> **Status: ✅ COMPLETE** (January 11-12, 2026)

---

## Data Summary

| Dataset | Records | Size | Location |
|---------|---------|------|----------|
| Products | 101 | 61 KB | Bronze → Silver → Gold |
| Dealers | 100 | 8 KB | Bronze → Silver → Gold |
| Sales | 562,585 | 86 MB | Bronze → Silver → Gold |
| Inventory | 126,392 | 10 MB | Bronze → Silver → Gold |
| **Total** | **~689K** | **97 MB** | - |

---

## ADLS Storage Structure

```
adlsstihlanalytics/stihl-analytics-data/
├── bronze/
│   ├── products_raw/
│   │   └── products.json
│   ├── dealers_raw/
│   │   └── dealers.csv
│   ├── sales_raw/
│   │   ├── sales_001.csv
│   │   ├── sales_002.csv
│   │   ├── sales_003.csv
│   │   ├── sales_004.csv
│   │   ├── sales_005.csv
│   │   └── sales_006.csv
│   └── inventory_raw/
│       ├── inventory_001.csv
│       ├── inventory_002.csv
│       └── inventory_003.csv
├── silver/
└── gold/
```

---

## Product Catalog (101 Products)

### Category Distribution

| Category | Count | Examples |
|----------|-------|----------|
| Accessories | 24 | Chains, bars, batteries, PPE |
| Chainsaws | 21 | MS 170, MS 271, MS 500i |
| Trimmers | 14 | FS 38, FS 91 R, FSA 130 |
| Blowers | 13 | BG 50, BR 600, BGA 100 |
| Hedge Trimmers | 12 | HS 45, HSA 86, HL 94 |
| Lawn Mowers | 10 | RM 443, RMA 510, iMOW |
| Multi-System | 7 | KM 56, KMA 130 |

### Power Types
- Gas: 56 products
- Battery: 38 products
- Accessory: 7 products

---

## Dealer Network (100 Dealers)

### Regional Distribution

| Region | Dealers | Percentage |
|--------|---------|------------|
| Southwest | 25 | 25% |
| Southeast | 22 | 22% |
| Midwest | 20 | 20% |
| Northeast | 18 | 18% |
| West | 15 | 15% |

### Dealer Types
- Authorized Dealer: 66
- Premium Dealer: 23
- Service Center: 11

---

## Sales Transactions (562,585 Records)

### Date Range
- Start: January 1, 2024
- End: December 31, 2025
- Duration: 24 months

### Key Metrics
- Total Revenue: $394,927,842.99
- Total Units: 816,913
- Avg Transaction: $701.99

### Seasonal Weights (Monthly)
| Month | Weight | Description |
|-------|--------|-------------|
| Jan | 0.6 | Winter slow |
| Feb | 0.7 | - |
| Mar | 1.2 | Spring start |
| Apr | 1.5 | Peak season |
| May | 1.5 | Peak season |
| Jun | 1.3 | Summer |
| Jul | 0.7 | Summer slow |
| Aug | 0.7 | Summer slow |
| Sep | 1.2 | Fall start |
| Oct | 1.3 | Fall |
| Nov | 1.4 | Pre-holiday |
| Dec | 0.8 | Holiday |

---

## Inventory Snapshots (126,392 Records)

### Configuration
- Sample Frequency: Every 3 days
- Products Tracked: 37 key products
- Warehouses: 13 across 5 regions

### Status Distribution
| Status | Count | Percentage |
|--------|-------|------------|
| NORMAL | 74,092 | 58.6% |
| LOW | 30,909 | 24.5% |
| CRITICAL | 20,019 | 15.8% |
| OUT_OF_STOCK | 1,372 | 1.1% |

### Warehouses by Region
- Southwest: WH-TX-01, WH-TX-02, WH-AZ-01
- Southeast: WH-FL-01, WH-GA-01, WH-NC-01
- Midwest: WH-OH-01, WH-IL-01, WH-MI-01
- Northeast: WH-NY-01, WH-PA-01
- West: WH-CA-01, WH-CA-02, WH-WA-01

---

## Injected Anomalies (Demo Scenarios)

### 🌀 Hurricane Texas (Jun 10-20, 2024)
| Metric | Value |
|--------|-------|
| Region | Southwest (TX only) |
| Category | Chainsaws |
| Impact | +280% sales spike |
| Verified | 444 vs 158 normal transactions |

### 🛒 Black Friday 2024 (Nov 25-30, 2024)
| Metric | Value |
|--------|-------|
| Region | All regions |
| Category | All products |
| Impact | +290% sales spike |
| Verified | 17,145 vs 5,857 normal transactions |

### 📦 Supply Disruption (Aug 2024)
| Metric | Value |
|--------|-------|
| Region | All regions |
| Category | Blowers |
| Impact | -60% sales drop |
| Verified | 1,199 vs 3,003 July transactions (0.4x) |

### ⚠️ MS-271 Stockout (Sep 1 - Oct 15, 2024)
| Metric | Value |
|--------|-------|
| Region | Southwest |
| Product | MS-271 Farm Boss |
| Impact | 5% normal stock |
| Verified | 45/45 snapshots critical/OOS |

### 📈 FS-91 Overstock (Oct - Dec 2024)
| Metric | Value |
|--------|-------|
| Region | Northeast |
| Product | FS-91 R Trimmer |
| Impact | 300% normal stock |

---

## Data Generation Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| `generate_all.py` | Master runner | All files |
| `generate_products.py` | Product catalog | products.json |
| `generate_dealers.py` | Dealer network | dealers.csv |
| `generate_sales.py` | Transactions | sales_*.csv |
| `generate_inventory.py` | Snapshots | inventory_*.csv |
| `upload_to_adls.py` | ADLS upload | - |

### Running Data Generation
```powershell
cd data\synthetic
python generate_all.py
python upload_to_adls.py
```

---

## Databricks Tables

### Bronze Schema (Raw)
```sql
dbw_stihl_analytics.bronze.products
dbw_stihl_analytics.bronze.dealers
dbw_stihl_analytics.bronze.sales
dbw_stihl_analytics.bronze.inventory
```

### Silver Schema (Cleaned)
```sql
dbw_stihl_analytics.silver.products
dbw_stihl_analytics.silver.dealers
dbw_stihl_analytics.silver.sales
dbw_stihl_analytics.silver.inventory
```

### Gold Schema (Aggregated)
```sql
dbw_stihl_analytics.gold.monthly_sales
dbw_stihl_analytics.gold.product_performance
dbw_stihl_analytics.gold.dealer_performance
dbw_stihl_analytics.gold.inventory_status
```

---

## ✅ Checklist (Completed)

- [x] Generate products.json (101 products)
- [x] Generate dealers.csv (100 dealers)
- [x] Generate sales transactions (562K records)
- [x] Generate inventory snapshots (126K records)
- [x] Inject anomalies for demo scenarios
- [x] Upload to ADLS Bronze layer
- [x] Create Bronze Delta tables
- [x] Transform to Silver tables
- [x] Aggregate to Gold tables

---

## Related Documents

- [PROJECT-MASTER.md](../PROJECT-MASTER.md) - Main project hub
- [DATABRICKS.md](../databricks/DATABRICKS.md) - ETL notebooks
- [INFRASTRUCTURE.md](../infrastructure/INFRASTRUCTURE.md) - Storage setup

---

*Last Updated: January 12, 2026*
