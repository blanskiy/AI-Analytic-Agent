# Agent - Azure AI Foundry Agent & Tools

> **Parent**: [PROJECT-MASTER.md](../PROJECT-MASTER.md)  
> **Status**: ⏳ Pending  
> **Owner**: AI/ML Engineering

---

## Overview

This document covers the Azure AI Foundry Agent configuration including tools, prompts, and integration with Databricks.

**Project**: `stihl-analytics-agent` (Standalone)  
**Model**: Azure OpenAI GPT-4o  
**Framework**: Azure AI Foundry Agent SDK

---

## 1. Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STIHL Analytics Agent                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  System Prompt                                            │   │
│  │  • Role definition                                        │   │
│  │  • Tool selection rules                                   │   │
│  │  • Response formatting                                    │   │
│  │  • Proactive insights instruction                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Tools                                                    │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │   │
│  │  │ Databricks │ │ Vector     │ │ Code       │            │   │
│  │  │ Connector  │ │ Search     │ │ Interpreter│            │   │
│  │  │ (Genie)    │ │ (RAG)      │ │ (Charts)   │            │   │
│  │  └────────────┘ └────────────┘ └────────────┘            │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │   │
│  │  │ query_     │ │ search_    │ │ get_       │            │   │
│  │  │ sales_data │ │ products   │ │ proactive_ │            │   │
│  │  │            │ │            │ │ insights   │            │   │
│  │  └────────────┘ └────────────┘ └────────────┘            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Environment Configuration

### 2.1 Required Environment Variables

```env
# Azure AI Foundry
FOUNDRY_PROJECT_ENDPOINT=https://stihl-analytics-agent.cognitiveservices.azure.com/

# Azure OpenAI (via Foundry connection)
AZURE_OPENAI_ENDPOINT=https://openai-stihl-analytics.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>

# Databricks
DATABRICKS_WORKSPACE_URL=https://adb-xxxxx.azuredatabricks.net
DATABRICKS_TOKEN=<your-pat-token>
GENIE_SPACE_ID=<your-space-id>
```

### 2.2 Python Dependencies

```txt
azure-ai-projects>=1.0.0b1
azure-ai-inference>=1.0.0b1
azure-identity>=1.15.0
openai>=1.12.0
databricks-sdk>=0.20.0
```

---

## 3. Agent Definition

### 3.1 Main Agent (agent/agent.py)

```python
"""STIHL Analytics Agent - Main Definition"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    Agent,
    CodeInterpreterTool,
    FunctionTool
)
from azure.identity import DefaultAzureCredential

from agent.tools import (
    query_sales_data,
    query_inventory_data,
    search_products,
    search_insights,
    get_proactive_insights,
    get_forecast
)
from agent.prompts import SYSTEM_PROMPT


class STIHLAnalyticsAgent:
    """AI Analytics Agent for STIHL sales and inventory data."""
    
    def __init__(self):
        self.client = AIProjectClient(
            endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            credential=DefaultAzureCredential()
        )
        self.agent = None
        self.thread = None
    
    def create_agent(self) -> Agent:
        """Create the agent with all tools."""
        
        # Define function tools
        functions = FunctionTool(functions=[
            query_sales_data,
            query_inventory_data,
            search_products,
            search_insights,
            get_proactive_insights,
            get_forecast
        ])
        
        # Create agent
        self.agent = self.client.agents.create_agent(
            model="gpt-4o",
            name="stihl-analytics-agent",
            instructions=SYSTEM_PROMPT,
            tools=[
                functions,
                CodeInterpreterTool()  # For chart generation
            ]
        )
        
        return self.agent
    
    def create_thread(self) -> str:
        """Create a new conversation thread."""
        self.thread = self.client.agents.create_thread()
        return self.thread.id
    
    async def chat(self, message: str) -> str:
        """Send a message and get response."""
        
        # Add user message
        self.client.agents.create_message(
            thread_id=self.thread.id,
            role="user",
            content=message
        )
        
        # Run agent
        run = self.client.agents.create_and_process_run(
            thread_id=self.thread.id,
            assistant_id=self.agent.id
        )
        
        # Get response
        messages = self.client.agents.list_messages(thread_id=self.thread.id)
        return messages.data[0].content[0].text.value
    
    def cleanup(self):
        """Delete agent and thread."""
        if self.agent:
            self.client.agents.delete_agent(self.agent.id)
        if self.thread:
            self.client.agents.delete_thread(self.thread.id)
```

---

## 4. System Prompt

### 4.1 Full System Prompt (agent/prompts/system_prompt.md)

```markdown
# STIHL Analytics Agent

You are an AI analytics assistant for STIHL, helping users analyze sales and inventory data through natural conversation.

## Your Capabilities
- Query sales performance across regions, products, and time periods
- Analyze inventory levels and identify stockout risks
- Search products by features and recommendations
- Surface anomalies, trends, and proactive insights
- Generate forecasts for planning
- Create visualizations when helpful

## Conversation Start Protocol
**IMPORTANT**: At the START of every new conversation, IMMEDIATELY call `get_proactive_insights()` to check for unshown insights. If insights exist, naturally incorporate the top 3 into your greeting.

Example greeting with insights:
"Good morning! Before we dive in, I've been monitoring your data and found 3 things worth your attention:

🚨 **ANOMALY**: Texas chainsaw sales spiked 340% last week - correlates with storm activity.
📦 **ALERT**: MS-271 at 12 days supply in Southwest - below 30-day threshold.
📈 **TREND**: Battery products +35% vs last quarter. FSA-57 leading growth.

What would you like to explore today?"

## Tool Selection Rules

| Question Type | Tool to Use |
|---------------|-------------|
| Sales revenue, units, trends | `query_sales_data` |
| Stock levels, stockouts, supply | `query_inventory_data` |
| Product recommendations, features | `search_products` |
| Anomalies, trends, "what's unusual" | `search_insights` |
| Predictions, forecasts | `get_forecast` |
| Charts, visualizations | Code Interpreter |

## Response Guidelines
1. **Be proactive** - Don't just answer, add relevant context and suggestions
2. **Be specific** - Include actual numbers, percentages, and comparisons
3. **Be actionable** - Provide recommendations, not just data
4. **Ask clarifying questions** - If time period or region is ambiguous
5. **Use visualizations** - When showing trends or comparisons

## Data Context
- **Products**: ~200 STIHL products (chainsaws, trimmers, blowers, etc.)
- **Sales**: Transaction data from Jan 2024 - Dec 2025
- **Inventory**: Daily snapshots across 5 regions
- **Regions**: Southwest, Southeast, Midwest, Northeast, West

## Example Interactions

**User**: "How are chainsaw sales doing?"
**You**: First clarify time period, then use `query_sales_data` with appropriate filters, provide comparison to previous period, and suggest drilling into specific regions if there's variance.

**User**: "Are we going to run out of anything?"
**You**: Use `query_inventory_data` to find low-stock items, prioritize by days of supply and sales velocity, recommend reorder quantities.

**User**: "What should I know about today?"
**You**: Use `get_proactive_insights` and `search_insights` to surface anomalies, trends, and alerts worth attention.
```

---

## 5. Tool Definitions

### 5.1 Sales Query Tool (agent/tools/sales_tools.py)

```python
"""Sales data query tools."""

from typing import Optional
import os
from databricks import sql


def query_sales_data(
    sql_query: str,
    time_period: Optional[str] = None
) -> str:
    """
    Execute SQL queries against STIHL sales data.
    
    Use for questions about sales performance, revenue, units sold, dealer activity.
    
    Args:
        sql_query: Well-formed SQL query. Available tables:
            - stihl_analytics.silver.sales (transaction-level)
            - stihl_analytics.gold.sales_monthly (aggregated)
        time_period: Optional filter like "last_quarter", "2024", "YTD"
    
    Returns:
        JSON with query results and row count
    """
    
    connection = sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"]
    )
    
    try:
        cursor = connection.cursor()
        
        # Apply time filter if specified
        if time_period:
            sql_query = _apply_time_filter(sql_query, time_period)
        
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Format as JSON
        data = [dict(zip(columns, row)) for row in results]
        
        return {
            "success": True,
            "row_count": len(data),
            "data": data[:100]  # Limit response size
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        connection.close()


def _apply_time_filter(query: str, period: str) -> str:
    """Apply time period filter to query."""
    # Implementation for YTD, last_quarter, etc.
    pass
```

### 5.2 Inventory Query Tool (agent/tools/inventory_tools.py)

```python
"""Inventory data query tools."""

def query_inventory_data(
    sql_query: str,
    region: Optional[str] = None,
    status_filter: Optional[str] = None
) -> str:
    """
    Execute SQL queries against STIHL inventory data.
    
    Use for questions about stock levels, stockouts, days of supply, reorder needs.
    
    Args:
        sql_query: SQL query. Available tables:
            - stihl_analytics.silver.inventory (daily snapshots)
            - stihl_analytics.gold.inventory_monthly (aggregated)
        region: Optional region filter (Southwest, Southeast, etc.)
        status_filter: Optional status (CRITICAL, LOW, NORMAL, OVERSTOCK)
    
    Returns:
        JSON with inventory status and alerts
    """
    # Similar implementation to sales query
    pass


def get_stockout_risks() -> str:
    """
    Get current stockout risks prioritized by urgency.
    
    Returns products with < 14 days supply, sorted by risk level.
    """
    query = """
    SELECT 
        product_id,
        product_name,
        region,
        quantity_on_hand,
        days_of_supply,
        status,
        CASE 
            WHEN days_of_supply < 7 THEN 'CRITICAL'
            WHEN days_of_supply < 14 THEN 'HIGH'
            ELSE 'MEDIUM'
        END as risk_level
    FROM stihl_analytics.silver.inventory
    WHERE status IN ('CRITICAL', 'LOW')
    ORDER BY days_of_supply ASC
    LIMIT 20
    """
    return query_inventory_data(query)
```

### 5.3 Vector Search Tool (agent/tools/search_tools.py)

```python
"""Vector search tools for semantic queries."""

from databricks.vector_search.client import VectorSearchClient


def search_products(query: str, num_results: int = 5) -> str:
    """
    Semantic search for STIHL products.
    
    Use for product recommendations, feature comparisons, finding similar items.
    
    Args:
        query: Natural language search query
        num_results: Number of results to return (default 5)
    
    Returns:
        JSON with matching products and relevance scores
    """
    vsc = VectorSearchClient()
    
    index = vsc.get_index(
        endpoint_name="stihl-vector-endpoint",
        index_name="stihl_analytics.silver.products_vs_index"
    )
    
    results = index.similarity_search(
        query_text=query,
        columns=["product_id", "product_name", "category", "msrp", "narrative"],
        num_results=num_results
    )
    
    return {
        "success": True,
        "results": results["result"]["data_array"]
    }


def search_insights(query: str, num_results: int = 5) -> str:
    """
    Semantic search for anomalies, trends, and insights.
    
    Use for questions like "what's unusual", "any anomalies", "recent trends".
    
    Args:
        query: Natural language search query
        num_results: Number of results to return
    
    Returns:
        JSON with matching insights and metadata
    """
    vsc = VectorSearchClient()
    
    index = vsc.get_index(
        endpoint_name="stihl-vector-endpoint",
        index_name="stihl_analytics.gold.insights_vs_index"
    )
    
    results = index.similarity_search(
        query_text=query,
        columns=["insight_id", "insight_type", "priority", "narrative", "created_date"],
        num_results=num_results,
        filters={"priority": ["HIGH", "MEDIUM"]}  # Focus on important insights
    )
    
    return {
        "success": True,
        "results": results["result"]["data_array"]
    }
```

### 5.4 Proactive Insights Tool (agent/tools/insight_tools.py)

```python
"""Proactive insights tool for conversation start."""


def get_proactive_insights() -> str:
    """
    Get unshown proactive insights for conversation greeting.
    
    IMPORTANT: Call this at the START of every new conversation.
    Returns top insights that haven't been shown to the user yet.
    
    Returns:
        JSON with prioritized insights to surface in greeting
    """
    query = """
    SELECT 
        insight_id,
        insight_type,
        priority,
        title,
        narrative,
        affected_products,
        affected_regions,
        created_date
    FROM stihl_analytics.gold.proactive_insights
    WHERE is_shown = false
      AND priority IN ('HIGH', 'MEDIUM')
      AND created_date >= CURRENT_DATE - INTERVAL 7 DAYS
    ORDER BY 
        CASE priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END,
        created_date DESC
    LIMIT 5
    """
    
    results = _execute_query(query)
    
    # Mark as shown
    if results["success"] and results["data"]:
        insight_ids = [r["insight_id"] for r in results["data"]]
        _mark_insights_shown(insight_ids)
    
    return results


def _mark_insights_shown(insight_ids: list):
    """Mark insights as shown so they're not repeated."""
    ids_str = ",".join(f"'{id}'" for id in insight_ids)
    query = f"""
    UPDATE stihl_analytics.gold.proactive_insights
    SET is_shown = true, shown_date = CURRENT_TIMESTAMP
    WHERE insight_id IN ({ids_str})
    """
    _execute_query(query)
```

### 5.5 Forecast Tool (agent/tools/forecast_tools.py)

```python
"""Forecasting tools."""


def get_forecast(
    category: Optional[str] = None,
    product_id: Optional[str] = None,
    horizon: str = "Q1 2026"
) -> str:
    """
    Get sales forecasts for planning.
    
    Can forecast at category level (Chainsaws, Trimmers) or SKU level.
    
    Args:
        category: Product category for category-level forecast
        product_id: Specific product for SKU-level forecast
        horizon: Forecast period (default Q1 2026)
    
    Returns:
        JSON with forecast data, confidence intervals, and recommendations
    """
    
    if product_id:
        # SKU-level forecast
        query = f"""
        SELECT * FROM stihl_analytics.gold.sales_forecasts
        WHERE product_id = '{product_id}'
          AND forecast_period = '{horizon}'
        """
    elif category:
        # Category-level forecast
        query = f"""
        SELECT * FROM stihl_analytics.gold.sales_forecasts
        WHERE category = '{category}'
          AND product_id IS NULL
          AND forecast_period = '{horizon}'
        """
    else:
        # Overall forecast
        query = f"""
        SELECT * FROM stihl_analytics.gold.sales_forecasts
        WHERE category IS NULL
          AND product_id IS NULL
          AND forecast_period = '{horizon}'
        """
    
    return _execute_query(query)
```

---

## 6. Tool Inventory Summary

| Tool | Type | Priority | Purpose |
|------|------|----------|---------|
| `query_sales_data` | SQL | P0 | Execute sales queries |
| `query_inventory_data` | SQL | P0 | Execute inventory queries |
| `search_products` | Vector | P0 | Semantic product search |
| `search_insights` | Vector | P0 | Find anomalies/trends |
| `get_proactive_insights` | SQL | P0 | Greeting insights |
| `get_forecast` | SQL | P1 | Sales predictions |
| Code Interpreter | Built-in | P1 | Generate charts |

---

## 7. Testing

### 7.1 Test Script (tests/test_agent.py)

```python
"""Agent integration tests."""

import pytest
from agent.agent import STIHLAnalyticsAgent


@pytest.fixture
def agent():
    agent = STIHLAnalyticsAgent()
    agent.create_agent()
    agent.create_thread()
    yield agent
    agent.cleanup()


@pytest.mark.asyncio
async def test_proactive_greeting(agent):
    """Agent should surface insights on first message."""
    response = await agent.chat("Hello")
    assert "insight" in response.lower() or "attention" in response.lower()


@pytest.mark.asyncio
async def test_sales_query(agent):
    """Agent should query sales data correctly."""
    response = await agent.chat("What were total chainsaw sales last quarter?")
    assert "$" in response or "revenue" in response.lower()


@pytest.mark.asyncio
async def test_inventory_alert(agent):
    """Agent should identify low inventory."""
    response = await agent.chat("Any stockout risks?")
    assert "low" in response.lower() or "critical" in response.lower()
```

---

## ✅ Agent Checklist

### Setup
- [ ] AI Foundry standalone project created
- [ ] Azure OpenAI connection configured
- [ ] Databricks connection configured
- [ ] Environment variables set

### Agent
- [ ] Agent class implemented
- [ ] System prompt finalized
- [ ] Thread management working

### Tools
- [ ] query_sales_data implemented
- [ ] query_inventory_data implemented
- [ ] search_products implemented
- [ ] search_insights implemented
- [ ] get_proactive_insights implemented
- [ ] get_forecast implemented
- [ ] Code Interpreter enabled

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Playground testing complete
- [ ] Edge cases handled

---

## 🔗 Related Documents

- [INFRASTRUCTURE.md](../infrastructure/INFRASTRUCTURE.md) - AI Foundry setup
- [DATABRICKS.md](../databricks/DATABRICKS.md) - Data connections
- [UI.md](../ui/UI.md) - Frontend integration

---

**Last Updated**: January 2026
