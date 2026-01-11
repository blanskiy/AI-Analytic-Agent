# AI Analytics Agent - Project Master

> **Purpose**: Master documentation hub linking all component specifications. Start here for project overview and navigate to detailed docs for each area.

**Repository**: [github.com/blanskiy/AI-Analytic-Agent](https://github.com/blanskiy/AI-Analytic-Agent)  
**Status**: 🟡 In Progress - Infrastructure Setup  
**Target**: 2-week sprint to demo-ready

---

## 🎯 Project Vision

Build an AI-powered analytics agent that **proactively surfaces insights** from sales and inventory data, demonstrating capabilities beyond traditional Power BI dashboards.

### Hero Moment
> "Tell me something I didn't know to ask about, that would take my analyst hours to discover in Power BI"

---

## 📁 Documentation Hierarchy

```
AI-Analytic-Agent/
│
├── 📄 PROJECT-MASTER.md          ← You are here
│
├── 📂 docs/
│   ├── 📄 CONTEXT-SUMMARY.md     → Full project context & decisions
│   ├── 📄 ARCHITECTURE.md        → System architecture diagrams
│   └── 📄 DEMO-SCRIPT.md         → 15-minute demo presentation
│
├── 📂 infrastructure/
│   └── 📄 INFRASTRUCTURE.md      → Azure resource setup & configuration
│
├── 📂 data/
│   └── 📄 DATA-LAYER.md          → Medallion architecture & synthetic data
│
├── 📂 databricks/
│   └── 📄 DATABRICKS.md          → Unity Catalog, notebooks, Vector Search
│
├── 📂 agent/
│   └── 📄 AGENT.md               → AI Foundry agent, tools, prompts
│
└── 📂 ui/
    └── 📄 UI.md                  → React frontend & visualizations
```

---

## 🔗 Quick Navigation

| Component | Document | Status | Description |
|-----------|----------|--------|-------------|
| **Context** | [docs/CONTEXT-SUMMARY.md](docs/CONTEXT-SUMMARY.md) | ✅ Complete | All confirmed decisions & specs |
| **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 📝 Draft | System diagrams & data flow |
| **Infrastructure** | [infrastructure/INFRASTRUCTURE.md](infrastructure/INFRASTRUCTURE.md) | 🔄 Active | Azure resources setup |
| **Data Layer** | [data/DATA-LAYER.md](data/DATA-LAYER.md) | ⏳ Pending | Medallion architecture |
| **Databricks** | [databricks/DATABRICKS.md](databricks/DATABRICKS.md) | ⏳ Pending | Unity Catalog, ETL, Vector Search |
| **Agent** | [agent/AGENT.md](agent/AGENT.md) | ⏳ Pending | AI Foundry agent & tools |
| **UI** | [ui/UI.md](ui/UI.md) | ⏳ Pending | React frontend |
| **Demo** | [docs/DEMO-SCRIPT.md](docs/DEMO-SCRIPT.md) | ⏳ Pending | Presentation script |

---

## 🏗️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Agent Framework** | Azure AI Foundry Agent SDK | Orchestration, function calling |
| **LLM** | Azure OpenAI GPT-4o | Reasoning, natural language |
| **Embeddings** | text-embedding-ada-002 | Vector representations |
| **Vector Search** | Databricks Mosaic AI | Semantic search |
| **Data Platform** | Azure Databricks Premium | Unity Catalog, SQL Warehouse |
| **Storage** | ADLS Gen2 | Medallion architecture |
| **UI (Week 1)** | AI Foundry Playground | Rapid prototyping |
| **UI (Week 2)** | React + Plotly | Interactive demo |

---

## 📅 Sprint Plan

| Day | Phase | Focus | Deliverable |
|-----|-------|-------|-------------|
| 1-2 | **Infrastructure** | Azure Setup | All resources provisioned |
| 2-3 | **Data** | Synthetic Data | 500K records in Bronze |
| 3-4 | **Databricks** | ETL Pipeline | Silver/Gold Delta tables |
| 5-6 | **Databricks** | Vector Search | Mosaic AI indexes |
| 7-8 | **Agent** | Core Agent | Basic tools working |
| 9-10 | **Agent** | Analytics | Anomaly + Forecast tools |
| 11-12 | **UI** | React App | Interactive charts |
| 13-14 | **Polish** | Demo Prep | End-to-end testing |

---

## ✅ Progress Tracker

### Phase 1: Infrastructure
- [x] Create GitHub repository
- [x] Set up project structure
- [ ] Provision Azure OpenAI (West US 2)
- [ ] Provision ADLS Gen2
- [ ] Provision Databricks Premium
- [ ] Create AI Foundry Standalone Project
- [ ] Configure connections

### Phase 2: Data Layer
- [ ] Generate synthetic products (~200)
- [ ] Generate synthetic sales (~500K)
- [ ] Generate synthetic inventory (~150K)
- [ ] Upload to ADLS Bronze layer

### Phase 3: Databricks
- [ ] Create Unity Catalog
- [ ] Bronze → Silver ETL notebooks
- [ ] Silver → Gold aggregation
- [ ] Create vectorized tables
- [ ] Configure Vector Search indexes
- [ ] Set up External Model Endpoint

### Phase 4: Agent
- [ ] Create agent with system prompt
- [ ] Implement query_sales_data tool
- [ ] Implement query_inventory_data tool
- [ ] Implement search_products tool
- [ ] Implement get_proactive_insights tool
- [ ] Test in Playground

### Phase 5: UI & Demo
- [ ] Create React app scaffold
- [ ] Implement chat interface
- [ ] Add Plotly visualizations
- [ ] Rehearse demo script
- [ ] Record demo video

---

## 🔑 Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| AI Foundry Project Type | **Standalone** | Required for Databricks connector |
| Region | **West US 2** | Co-location with existing resources |
| Embedding Delivery | **Databricks External Model** | Unified governance |
| Forecasting Level | **Category + SKU** | Dual granularity for flexibility |
| Proactive Insights | **Pre-computed daily** | Fast response, hero feature |

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Query Response Time | < 5 seconds |
| Proactive Insights Accuracy | > 85% relevance |
| Demo Duration | 15 minutes |
| Stakeholder Reaction | "Wow, it told me without asking!" |

---

## 🚀 Quick Start

### For New AI Chat Sessions

Copy this to establish context:
```
I'm working on the AI-Analytic-Agent project. 
See PROJECT-MASTER.md for overview and navigation.
Current task: [specific task from progress tracker]
```

### For Development
```bash
# Clone repository
git clone https://github.com/blanskiy/AI-Analytic-Agent.git
cd AI-Analytic-Agent

# Set up Python environment
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your Azure credentials
```

---

## 📞 Related Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Databricks Mosaic AI](https://docs.databricks.com/en/generative-ai/vector-search.html)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)

---

**Last Updated**: January 2026  
**Author**: Bruce Lanskiy  
**Portfolio Target**: Microsoft, Apple, Tesla AI Architect roles
