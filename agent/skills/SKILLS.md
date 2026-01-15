# STIHL Analytics Agent - Skills Framework

## Overview

The Skills Framework provides intelligent query routing and context-aware prompt enhancement for the STIHL Analytics Agent. Each skill encapsulates domain-specific knowledge, tools, and response guidelines.

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                      SKILL ROUTER                            │
│  1. Pattern matching against all skills                      │
│  2. Confidence scoring                                       │
│  3. Priority-based selection                                 │
│  4. Return best match or None                                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    SELECTED SKILL                            │
│  • Enhanced system prompt injection                          │
│  • Filtered tool list                                        │
│  • Domain-specific context                                   │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
Azure OpenAI → Tool Calls → Response
```

## Available Skills (7 Total)

### Core Skills

| Skill | Name | Priority | Tools | Description |
|-------|------|----------|-------|-------------|
| **Insights Advisor** | `insights_advisor` | 25 | get_proactive_insights, detect_anomalies_realtime, get_daily_briefing | Proactive alerts, anomalies, briefings |
| **Product Expert** | `product_expert` | 20 | search_products, compare_products, get_product_recommendations | RAG-based semantic product search |
| **Sales Analyst** | `sales_analyst` | 15 | query_sales_data | Revenue, trends, rankings |
| **Inventory Analyst** | `inventory_analyst` | 15 | query_inventory_data | Stock levels, stockouts |

### Extended Skills (Phase 5d)

| Skill | Name | Priority | Tools | Description |
|-------|------|----------|-------|-------------|
| **Forecast Analyst** | `forecast_analyst` | 18 | get_sales_forecast | Predictions, projections, seasonal patterns |
| **Trend Analyst** | `trend_analyst` | 16 | analyze_trends | YoY, MoM, growth rates, momentum |
| **Dealer Analyst** | `dealer_analyst` | 15 | query_dealer_data | Dealer performance, network coverage |

## Priority System

Higher priority skills are checked first and win ties in confidence scoring:

1. **25** - Insights Advisor (greetings, anomalies get priority)
2. **20** - Product Expert (RAG queries)
3. **18** - Forecast Analyst (future-focused queries)
4. **16** - Trend Analyst (comparison queries)
5. **15** - Sales, Inventory, Dealer (standard analysis)

## Skill Details

### Insights Advisor
**Triggers:** Greetings, "good morning", "what should I know", "anomalies", "alerts", "briefing"

**Example Queries:**
- "Good morning!"
- "What should I know today?"
- "Any anomalies in March 2024?"
- "Give me a daily briefing"

### Product Expert (RAG)
**Triggers:** Product names, "best for", "recommend", "compare products", features

**Example Queries:**
- "What chainsaw is best for professionals?"
- "Compare the MS 461 and MS 500i"
- "Show me battery-powered blowers under 15 lbs"

### Sales Analyst
**Triggers:** Revenue, sales, top products, rankings, quarterly performance

**Example Queries:**
- "What was total revenue in 2024?"
- "Top 10 products by sales"
- "Regional breakdown for Q3"

### Inventory Analyst
**Triggers:** Stock, inventory, low stock, stockouts, days of supply

**Example Queries:**
- "Products running low on stock?"
- "Show me critical inventory items"
- "Days of supply for chainsaws"

### Dealer Analyst
**Triggers:** Dealer, dealership, partner, territory, coverage

**Example Queries:**
- "Who are our top dealers?"
- "Show me dealer performance by region"
- "Where do we have coverage gaps?"
- "How many flagship dealers do we have?"

### Forecast Analyst
**Triggers:** Forecast, predict, projection, next month/quarter, seasonal

**Example Queries:**
- "What's the sales forecast for next quarter?"
- "Project revenue through year end"
- "What are our seasonal patterns?"
- "When is our peak season?"

### Trend Analyst
**Triggers:** YoY, MoM, growth rate, momentum, vs last year, trend

**Example Queries:**
- "How does this year compare to last year?"
- "Show me YoY growth by category"
- "Is momentum picking up?"
- "Month-over-month change in revenue"

## Routing Examples

| Query | Skill | Confidence | Reason |
|-------|-------|------------|--------|
| "Good morning!" | insights_advisor | 0.9 | Greeting pattern |
| "What chainsaw is best for pros?" | product_expert | 0.85 | Product + recommendation |
| "Total revenue for 2024" | sales_analyst | 0.8 | Revenue + time period |
| "Products running low?" | inventory_analyst | 0.8 | Stock level query |
| "Who are our top dealers?" | dealer_analyst | 0.8 | Dealer + ranking |
| "Sales forecast for Q2?" | forecast_analyst | 0.85 | Forecast + time |
| "YoY growth rate?" | trend_analyst | 0.85 | YoY pattern |

## Adding New Skills

1. **Create skill class** in `agent/skills/`:
```python
from .base_skill import BaseSkill

class NewSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "skill_name"
    
    @property
    def triggers(self) -> list[str]:
        return [r"pattern1", r"pattern2"]
    
    @property
    def tools(self) -> list[str]:
        return ["tool_name"]
    
    @property
    def system_prompt(self) -> str:
        return "Skill-specific guidance..."
```

2. **Create tool** in `agent/tools/`:
```python
def new_tool(**kwargs) -> str:
    # Implementation
    return json.dumps(result)

TOOL_DEFINITION = {...}
```

3. **Register** in `router.py`:
```python
from .new_skill import NewSkill
self.register(NewSkill())
```

4. **Export** in `tools/__init__.py`

## Testing

```bash
# Test all skills
python -m tests.test_skills
python -m tests.test_new_skills

# Test routing interactively
python -c "
from agent.skills import get_router
router = get_router()
print(router.explain_routing('Your query here'))
"
```

## Integration with Agent

The `agent_realtime.py` integrates skills via:

```python
# In chat() method:
skill_match = self.router.route(user_message)
if skill_match:
    enhanced_prompt = self.router.get_prompt_for_skill(
        skill_match.skill_name, 
        BASE_SYSTEM_PROMPT
    )
    self._update_system_prompt(enhanced_prompt)
```

This enables:
- **Dynamic prompt enhancement** based on query type
- **Tool filtering** to only relevant tools per skill
- **Logging** of routing decisions for debugging

---

*Last Updated: January 14, 2025*
*Phase 5d - Extended Skills (Dealer, Forecast, Trend)*
