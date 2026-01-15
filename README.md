# Agent Tools

This directory contains all tool implementations for the STIHL Analytics Agent. Tools are callable functions that the Azure OpenAI function calling mechanism can invoke based on user queries.

## Tool Categories

### SQL-Based Tools (Quantitative Data)

These tools query Databricks SQL Warehouse for metrics and aggregated data.

| File | Tool | Description |
|------|------|-------------|
| `sales_tools.py` | `query_sales_data` | Revenue, trends, top products, regional analysis |
| `inventory_tools.py` | `query_inventory_data` | Stock levels, stockouts, days of supply |
| `insights_tools.py` | `get_proactive_insights` | Pre-computed anomalies from gold.proactive_insights |
| `insights_tools.py` | `detect_anomalies_realtime` | On-demand Z-score anomaly detection |
| `insights_tools.py` | `get_daily_briefing` | Combined metrics + top insights |

### RAG-Based Tools (Qualitative Data)

These tools use Databricks Vector Search for semantic product queries.

| File | Tool | Description |
|------|------|-------------|
| `rag_tools.py` | `search_products` | Semantic search with optional filters |
| `rag_tools.py` | `compare_products` | Side-by-side product comparison |
| `rag_tools.py` | `get_product_recommendations` | Use case-based recommendations |

## Tool Registry

The `__init__.py` file exports two key items:

```python
from agent.tools import TOOL_FUNCTIONS, TOOL_DEFINITIONS

# TOOL_FUNCTIONS: Dict mapping tool names to callable functions
# TOOL_DEFINITIONS: List of OpenAI function definitions for the API
```

## Adding New Tools

1. Create a new file (e.g., `new_tools.py`)
2. Implement tool function(s) with proper type hints and docstrings
3. Define `NEW_TOOL_DEFINITIONS` list with OpenAI function schema
4. Export in `__init__.py`:

```python
from .new_tools import new_tool, NEW_TOOL_DEFINITIONS

TOOL_FUNCTIONS = {
    # ... existing tools ...
    "new_tool": new_tool,
}

TOOL_DEFINITIONS = (
    # ... existing definitions ...
    NEW_TOOL_DEFINITIONS
)
```

## Tool Response Format

All tools return JSON strings with consistent structure:

```json
{
  "status": "success" | "error" | "no_results",
  "message": "Optional message",
  "data": { ... }
}
```

## Testing

```bash
# Test all tools
python -m tests.test_tools

# Test RAG tools specifically
python -m tests.test_rag_tools
```

## Dependencies

- `databricks-sql-connector`: For SQL queries
- `databricks-vectorsearch`: For RAG/Vector Search
- Connection configured via `agent.databricks_client`
