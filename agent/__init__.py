"""
STIHL Analytics Agent package.

Note: agent.py orchestrator requires Azure AI Foundry SDK setup.
Import tools directly for testing.
"""

from agent.databricks_client import DatabricksClient, execute_query

__all__ = [
    "DatabricksClient",
    "execute_query",
]

# Lazy import for agent orchestrator (requires Azure AI Foundry)
def create_agent():
    """Create agent - requires Azure AI Foundry SDK."""
    from agent.agent import STIHLAnalyticsAgent, create_agent as _create
    return _create()
