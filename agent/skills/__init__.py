"""
Skills package for STIHL Analytics Agent.

Skills encapsulate domain-specific knowledge and routing logic,
enabling the agent to intelligently route queries to appropriate
tools and provide contextually relevant responses.

## Available Skills

| Skill | Type | Purpose |
|-------|------|---------|
| ProductSkill | RAG | Product search, comparisons, recommendations |
| SalesSkill | SQL | Revenue, trends, rankings |
| InventorySkill | SQL | Stock levels, stockouts, days of supply |
| InsightsSkill | SQL | Anomalies, alerts, daily briefings |

## Usage

```python
from agent.skills import get_router, route_query

# Route a query
match = route_query("What chainsaw is best for professionals?")
if match:
    print(f"Skill: {match.skill_name}")
    print(f"Tools: {match.tools_available}")

# Get full router for advanced usage
router = get_router()
skill = router.get_skill("product_expert")
enhanced_prompt = skill.get_enhanced_prompt(base_prompt)
```

## Architecture

```
User Query
    ↓
SkillRouter.route()
    ↓
Pattern Matching (regex triggers)
    ↓
Best Match Selection (confidence + priority)
    ↓
Skill.get_enhanced_prompt()
    ↓
Agent executes with skill context
```
"""

from .base_skill import BaseSkill, SkillMatch
from .product_skill import ProductSkill
from .sales_skill import SalesSkill
from .inventory_skill import InventorySkill
from .insights_skill import InsightsSkill
from .router import SkillRouter, get_router, route_query

__all__ = [
    # Base classes
    "BaseSkill",
    "SkillMatch",
    
    # Concrete skills
    "ProductSkill",
    "SalesSkill", 
    "InventorySkill",
    "InsightsSkill",
    
    # Router
    "SkillRouter",
    "get_router",
    "route_query",
]
