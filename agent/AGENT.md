# Agent Architecture

> **Parent Document:** [PROJECT-MASTER.md](../PROJECT-MASTER.md)  
> **Last Updated:** January 14, 2025  
> **Phase:** 5c - Skills Framework

## Overview

The STIHL Analytics Agent is an AI-powered conversational interface that provides natural language access to sales analytics, inventory management, proactive insights, and product information.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STIHL ANALYTICS AGENT                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   USER QUERY                                                             │
│       ↓                                                                  │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      SKILL ROUTER                                │   │
│   │   Pattern matching → Confidence scoring → Skill selection        │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│       ↓                                                                  │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    AZURE OPENAI (gpt-4o-mini)                    │   │
│   │   System prompt + Skill enhancement + Function definitions       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│       ↓                                                                  │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                      TOOL EXECUTION                              │   │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│   │   │  SQL Tools   │  │  RAG Tools   │  │Insight Tools │          │   │
│   │   │  (Sales,     │  │  (Product    │  │  (Anomaly,   │          │   │
│   │   │  Inventory)  │  │   Search)    │  │   Briefing)  │          │   │
│   │   └──────────────┘  └──────────────┘  └──────────────┘          │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│       ↓                                    ↓                             │
│   ┌──────────────────┐          ┌──────────────────┐                    │
│   │  Databricks SQL  │          │  Databricks      │                    │
│   │  Warehouse       │          │  Vector Search   │                    │
│   └──────────────────┘          └──────────────────┘                    │
│       ↓                                                                  │
│   NATURAL LANGUAGE RESPONSE                                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
agent/
├── __init__.py
├── agent_realtime.py      # Main orchestrator
├── databricks_client.py   # SQL warehouse connection
├── AGENT.md              # This documentation
│
├── prompts/
│   ├── __init__.py
│   └── system_prompt.py   # Base system prompt
│
├── skills/                # Skill-based routing
│   ├── __init__.py
│   ├── base_skill.py      # BaseSkill abstract class
│   ├── router.py          # SkillRouter
│   ├── product_skill.py   # RAG-based (Vector Search)
│   ├── sales_skill.py     # SQL-based
│   ├── inventory_skill.py # SQL-based
│   ├── insights_skill.py  # SQL-based
│   └── SKILLS.md         # Skills documentation
│
└── tools/                 # Tool implementations
    ├── __init__.py        # Tool registry
    ├── sales_tools.py
    ├── inventory_tools.py
    ├── insights_tools.py
    ├── rag_tools.py       # Vector Search tools
    └── README.md
```

## Components

### 1. Agent Orchestrator (`agent_realtime.py`)

The main entry point that:
- Accepts user queries
- Routes through skill system
- Calls Azure OpenAI with function definitions
- Executes tool calls
- Returns natural language responses

```python
# Run the agent
python -m agent.agent_realtime
```

### 2. Skill Router (`skills/router.py`)

Routes queries to specialized skills based on pattern matching:

| Query Type | Skill | Backend |
|------------|-------|---------|
| Product features, recommendations | `product_expert` | Vector Search |
| Revenue, sales metrics | `sales_analyst` | SQL |
| Stock levels, stockouts | `inventory_analyst` | SQL |
| Alerts, anomalies, briefings | `insights_advisor` | SQL |

See [skills/SKILLS.md](skills/SKILLS.md) for detailed skill documentation.

### 3. Tools (`tools/`)

Eight tools available for function calling:

| Tool | Type | Purpose |
|------|------|---------|
| `query_sales_data` | SQL | Revenue, trends, rankings |
| `query_inventory_data` | SQL | Stock levels, stockouts |
| `get_proactive_insights` | SQL | Pre-computed alerts |
| `detect_anomalies_realtime` | SQL | On-demand Z-score analysis |
| `get_daily_briefing` | SQL | Daily summary |
| `search_products` | RAG | Semantic product search |
| `compare_products` | SQL | Side-by-side comparison |
| `get_product_recommendations` | RAG | Use case recommendations |

See [tools/README.md](tools/README.md) for tool documentation.

### 4. Databricks Client (`databricks_client.py`)

Handles connection to Databricks SQL Warehouse:
- Connection pooling
- Query execution
- Result formatting

## Data Flow

### SQL Query Flow
```
User: "What's our total revenue?"
    ↓
SkillRouter → SalesSkill (confidence: 0.85)
    ↓
Azure OpenAI → calls query_sales_data(query_type="summary")
    ↓
Databricks SQL → SELECT SUM(total_revenue) FROM gold.monthly_sales
    ↓
Response: "Total revenue is $394.9M across 24 months..."
```

### RAG Query Flow
```
User: "What chainsaw is best for professionals?"
    ↓
SkillRouter → ProductSkill (confidence: 0.90)
    ↓
Azure OpenAI → calls search_products(query="professional chainsaw")
    ↓
Databricks Vector Search → similarity_search with BGE-Large
    ↓
Response: "For professional use, I recommend the MS 661 C-M..."
```

## Configuration

Environment variables (`.env`):

```bash
# Databricks
DATABRICKS_HOST=your-workspace.azuredatabricks.net
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-id
DATABRICKS_TOKEN=your-token
DATABRICKS_CATALOG=dbw_stihl_analytics

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT_GPT=gpt-4o-mini
```

## Testing

```bash
# Test all tools
python -m tests.test_tools

# Test RAG tools specifically
python -m tests.test_rag_tools

# Test skill routing
python -m tests.test_skills

# Run interactive agent
python -m agent.agent_realtime
```

## Related Documentation

- [skills/SKILLS.md](skills/SKILLS.md) - Skill framework details
- [tools/README.md](tools/README.md) - Tool implementations
- [../PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) - Project overview
- [../PROJECT-MASTER.md](../PROJECT-MASTER.md) - Master documentation
