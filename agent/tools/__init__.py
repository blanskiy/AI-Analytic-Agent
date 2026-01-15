"""
Agent tools registry - exports all tool functions and definitions.

This module provides a unified interface for all agent tools.
"""

from .sales_tools import query_sales_data
from .inventory_tools import query_inventory_data
from .insights_tools import (
    get_proactive_insights,
    detect_anomalies_realtime,
    get_daily_briefing
)
from .rag_tools import (
    search_products,
    compare_products,
    get_product_recommendations,
    RAG_TOOL_DEFINITIONS,
    RAG_TOOL_FUNCTIONS
)


# Tool definitions for Azure OpenAI function calling
# (Existing tools don't export definitions, so we define them here)
SALES_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "query_sales_data",
            "description": "Query STIHL sales data for revenue, units sold, trends, and rankings. Use for questions about sales performance, top products, dealer performance, or regional analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": ["summary", "top_products", "top_dealers", "trend", "by_category", "by_region"],
                        "description": "Type of sales analysis"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time filter: last_month, last_quarter, last_year, ytd, or specific (2024-Q1, 2024-06)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by product category"
                    },
                    "region": {
                        "type": "string",
                        "description": "Filter by region"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of results for ranking queries",
                        "default": 10
                    }
                },
                "required": ["query_type"]
            }
        }
    }
]

INVENTORY_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "query_inventory_data",
            "description": "Query STIHL inventory data for stock levels, stockouts, and days of supply. Use for questions about current inventory, low stock alerts, or regional stock distribution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": ["summary", "low_stock", "stockouts", "by_category", "by_region", "days_of_supply"],
                        "description": "Type of inventory analysis"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by product category"
                    },
                    "region": {
                        "type": "string",
                        "description": "Filter by region"
                    },
                    "status_filter": {
                        "type": "string",
                        "enum": ["CRITICAL", "LOW", "NORMAL"],
                        "description": "Filter by stock status"
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of results",
                        "default": 10
                    }
                },
                "required": ["query_type"]
            }
        }
    }
]

INSIGHTS_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_proactive_insights",
            "description": "Get proactive insights including anomalies, alerts, and trends. Call at conversation start or when user asks 'What should I know?' or 'Any updates?'",
            "parameters": {
                "type": "object",
                "properties": {
                    "insight_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by type: anomaly, stockout_risk, trend, forecast_alert, opportunity"
                    },
                    "severity_filter": {
                        "type": "string",
                        "enum": ["critical", "warning", "info"],
                        "description": "Filter by urgency"
                    },
                    "max_insights": {
                        "type": "integer",
                        "description": "Maximum insights to return",
                        "default": 5
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_anomalies_realtime",
            "description": "Run real-time anomaly detection using Z-score analysis on specific metrics and time periods.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "enum": ["revenue", "units", "transactions"],
                        "description": "Metric to analyze"
                    },
                    "group_by": {
                        "type": "string",
                        "enum": ["category", "region", "product"],
                        "description": "Dimension to group by"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Specific period to analyze (e.g., 2024-03)"
                    },
                    "z_threshold": {
                        "type": "number",
                        "description": "Z-score threshold for anomaly (default 2.0)",
                        "default": 2.0
                    }
                },
                "required": ["metric", "group_by"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_daily_briefing",
            "description": "Get a daily business briefing with key metrics and top insights. Use when user says 'Good morning' or asks for an overview.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


# Combined tool functions mapping
TOOL_FUNCTIONS = {
    "query_sales_data": query_sales_data,
    "query_inventory_data": query_inventory_data,
    "get_proactive_insights": get_proactive_insights,
    "detect_anomalies_realtime": detect_anomalies_realtime,
    "get_daily_briefing": get_daily_briefing,
    **RAG_TOOL_FUNCTIONS
}

# Combined tool definitions for Azure OpenAI
TOOL_DEFINITIONS = (
    SALES_TOOL_DEFINITIONS +
    INVENTORY_TOOL_DEFINITIONS +
    INSIGHTS_TOOL_DEFINITIONS +
    RAG_TOOL_DEFINITIONS
)

__all__ = [
    "TOOL_FUNCTIONS",
    "TOOL_DEFINITIONS",
    "query_sales_data",
    "query_inventory_data",
    "get_proactive_insights",
    "detect_anomalies_realtime",
    "get_daily_briefing",
    "search_products",
    "compare_products",
    "get_product_recommendations",
]
