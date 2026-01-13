"""
STIHL Analytics Agent Tools.
All tools for querying sales, inventory, and proactive insights.
"""

from agent.tools.sales_tools import (
    query_sales_data,
    SALES_TOOL_DEFINITION,
)
from agent.tools.inventory_tools import (
    query_inventory_data,
    INVENTORY_TOOL_DEFINITION,
)
from agent.tools.insights_tools import (
    get_proactive_insights,
    detect_anomalies_realtime,
    get_daily_briefing,
    PROACTIVE_INSIGHTS_TOOL_DEFINITION,
    DETECT_ANOMALIES_TOOL_DEFINITION,
    DAILY_BRIEFING_TOOL_DEFINITION,
)

# All tool functions mapped by name
TOOL_FUNCTIONS = {
    "query_sales_data": query_sales_data,
    "query_inventory_data": query_inventory_data,
    "get_proactive_insights": get_proactive_insights,
    "detect_anomalies_realtime": detect_anomalies_realtime,
    "get_daily_briefing": get_daily_briefing,
}

# All tool definitions for Azure AI Foundry registration
TOOL_DEFINITIONS = [
    SALES_TOOL_DEFINITION,
    INVENTORY_TOOL_DEFINITION,
    PROACTIVE_INSIGHTS_TOOL_DEFINITION,
    DETECT_ANOMALIES_TOOL_DEFINITION,
    DAILY_BRIEFING_TOOL_DEFINITION,
]

__all__ = [
    "query_sales_data",
    "query_inventory_data",
    "get_proactive_insights",
    "detect_anomalies_realtime",
    "get_daily_briefing",
    "TOOL_FUNCTIONS",
    "TOOL_DEFINITIONS",
]
