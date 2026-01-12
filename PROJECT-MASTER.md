# STIHL Analytics Agent - Project Master

> **AI-Powered Analytics Agent for STIHL Dealership Network**
> Portfolio project demonstrating Azure AI Foundry, Databricks, and conversational analytics

---

## 🎯 Project Overview

An intelligent analytics agent that provides proactive insights, natural language querying, and forecasting for STIHL outdoor power equipment sales and inventory data.

**Target Audience:** Microsoft, Apple, Tesla AI Architect roles

---

## 📊 Current Status

| Phase | Status | Completed |
|-------|--------|-----------|
| Phase 1: Infrastructure | ✅ Complete | Jan 11, 2026 |
| Phase 2: Data Generation | ✅ Complete | Jan 11, 2026 |
| Phase 3: Databricks | ✅ Complete | Jan 12, 2026 |
| Phase 4: AI Agent | ⏳ Next | - |
| Phase 5: UI & Demo | 📝 Pending | - |

---

## 🏗️ Technology Stack

| Component | Technology | Status |
|-----------|------------|--------|
| AI Orchestration | Azure AI Foundry Agent SDK | ⏳ Pending |
| LLM | Azure OpenAI GPT-4o-mini | ✅ Deployed |
| Embeddings | text-embedding-ada-002 | ✅ Deployed |
| Data Platform | Databricks Unity Catalog | ✅ Configured |
| Storage | ADLS Gen2 (Medallion) | ✅ Configured |
| Vector Search | Mosaic AI Vector Search | ⏳ Pending |
| Frontend | React + Plotly (Week 2) | 📝 Pending |

---

## 🔗 Resource Endpoints

| Service | Endpoint |
|---------|----------|
| Azure OpenAI | `https://openai-stihl-analytics.openai.azure.com/` |
| ADLS Gen2 | `https://adlsstihlanalytics.dfs.core.windows.net/` |
| Databricks | `https://adb-7405610757175308.8.azuredatabricks.net` |
| AI Foundry | `https://stihl-analytics-agent-resource.services.ai.azure.com/` |

---

## 📁 Project Structure

```
ai-analytic-agent/
├── PROJECT-MASTER.md          ← You are here
├── .env                       # Local config (git-ignored)
├── .env.example               # Config template
├── requirements.txt
│
├── agent/                     # AI Agent code
│   └── AGENT.md              # Agent implementation guide
│
├── data/
│   ├── DATA-LAYER.md         # Data architecture docs
│   └── synthetic/            # Data generators
│       ├── generate_all.py
│       ├── generate_products.py
│       ├── generate_dealers.py
│       ├── generate_sales.py
│       ├── generate_inventory.py
│       └── upload_to_adls.py
│
├── databricks/
│   ├── DATABRICKS.md         # Databricks setup guide
│   └── notebooks/
│       ├── 01_bronze_ingestion.py
│       ├── 02_silver_transform.py
│       └── 03_gold_aggregation.py
│
├── docs/
│   ├── ARCHITECTURE.md       # System architecture
│   └── DEMO-SCRIPT.md        # 15-min demo script
│
├── infrastructure/
│   └── INFRASTRUCTURE.md     # Azure resource setup
│
├── tests/                    # Test files
│
└── ui/
    └── UI.md                 # Frontend specs
```

---

## ✅ Completed Work

### Phase 1: Infrastructure ✅
- [x] GitHub repository created
- [x] Project folder structure established
- [x] Azure OpenAI deployed (West US) - gpt-4o-mini, text-embedding-ada-002
- [x] ADLS Gen2 storage with medallion directories (bronze/silver/gold)
- [x] Databricks Premium workspace
- [x] AI Foundry standalone project
- [x] Managed Identity + RBAC for secure ADLS access
- [x] Environment configuration (.env)

### Phase 2: Data Generation ✅
- [x] Product catalog generator (101 STIHL products)
- [x] Dealer network generator (100 dealers, 5 regions)
- [x] Sales transaction generator (562K transactions)
- [x] Inventory snapshot generator (126K snapshots)
- [x] Injected anomalies (Hurricane TX, Black Friday, supply disruption)
- [x] Upload to ADLS Bronze layer (97 MB)

### Phase 3: Databricks ✅
- [x] Unity Catalog: `dbw_stihl_analytics`
- [x] Storage credential with Access Connector
- [x] External location: `stihl_adls_location`
- [x] Bronze layer: 4 raw Delta tables
- [x] Silver layer: 4 cleaned/typed Delta tables
- [x] Gold layer: 4 aggregated analytics tables
- [x] ETL notebooks committed to repo

### Phase 4: AI Agent ⏳ (Next)
- [ ] Create AI Foundry agent with system prompt
- [ ] Implement Databricks SQL tools
- [ ] Add proactive insights feature
- [ ] Vector search for semantic queries
- [ ] Test conversational interface

### Phase 5: UI & Demo 📝
- [ ] AI Foundry Playground testing
- [ ] React frontend (optional)
- [ ] Demo script rehearsal
- [ ] Portfolio documentation

---

## 📊 Data Summary

| Dataset | Records | Description |
|---------|---------|-------------|
| Products | 101 | STIHL chainsaws, trimmers, blowers, etc. |
| Dealers | 100 | Across 5 US regions |
| Sales | 562,585 | Jan 2024 - Dec 2025 transactions |
| Inventory | 126,392 | Daily snapshots with status |

### Injected Anomalies (for Demo)
| Anomaly | Type | Period | Details |
|---------|------|--------|---------|
| 🌀 Hurricane Texas | +280% spike | Jun 2024 | Chainsaw sales in TX |
| 🛒 Black Friday | +290% spike | Nov 2024/2025 | All products |
| 📦 Supply Disruption | -60% drop | Aug 2024 | Blower availability |
| ⚠️ MS-271 Stockout | Critical | Sep-Oct 2024 | Southwest region |

---

## 🗄️ Databricks Tables

### Bronze (Raw)
- `dbw_stihl_analytics.bronze.products`
- `dbw_stihl_analytics.bronze.dealers`
- `dbw_stihl_analytics.bronze.sales`
- `dbw_stihl_analytics.bronze.inventory`

### Silver (Cleaned)
- `dbw_stihl_analytics.silver.products`
- `dbw_stihl_analytics.silver.dealers`
- `dbw_stihl_analytics.silver.sales`
- `dbw_stihl_analytics.silver.inventory`

### Gold (Aggregated)
- `dbw_stihl_analytics.gold.monthly_sales`
- `dbw_stihl_analytics.gold.product_performance`
- `dbw_stihl_analytics.gold.dealer_performance`
- `dbw_stihl_analytics.gold.inventory_status`

---

## 🚀 Quick Start (New Chat Session)

When starting a new Claude session for Phase 4, provide this context:

```
I'm continuing the STIHL Analytics Agent project. Phases 1-3 are complete:

**Completed:**
- Azure OpenAI: openai-stihl-analytics (gpt-4o-mini, embeddings) - West US
- ADLS Gen2: adlsstihlanalytics with medallion architecture
- Databricks: dbw-stihl-analytics with Unity Catalog
- AI Foundry: stihl-analytics-agent project
- Data: 562K sales, 126K inventory in Delta tables

**Databricks Tables:**
- Catalog: dbw_stihl_analytics
- Schemas: bronze, silver, gold (4 tables each)

**Next: Phase 4 - AI Agent**
- Create agent with Azure AI Foundry SDK
- Connect to Databricks for SQL queries
- Implement proactive insights feature

See PROJECT-MASTER.md and AGENT.md for full details.
```

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [INFRASTRUCTURE.md](./infrastructure/INFRASTRUCTURE.md) | Azure resource setup |
| [DATA-LAYER.md](./data/DATA-LAYER.md) | Medallion architecture |
| [DATABRICKS.md](./databricks/DATABRICKS.md) | Unity Catalog & ETL |
| [AGENT.md](./agent/AGENT.md) | AI agent implementation |
| [ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System design |
| [DEMO-SCRIPT.md](./docs/DEMO-SCRIPT.md) | 15-minute presentation |
| [UI.md](./ui/UI.md) | Frontend specifications |

---

## 💰 Estimated Costs

| Resource | Monthly Cost |
|----------|-------------|
| Azure OpenAI (GPT-4o-mini) | ~$5-15 |
| ADLS Gen2 | ~$2-5 |
| Databricks (dev usage) | ~$50-100 |
| AI Foundry | ~$5-10 |
| **Total** | **~$60-130/month** |

---

*Last Updated: January 12, 2026*
