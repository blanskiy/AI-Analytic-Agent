# Skills Framework

> **Parent Document:** [AGENT.md](../AGENT.md)  
> **Last Updated:** January 14, 2025  
> **Phase:** 5c - Skills Framework

## Overview

Skills encapsulate domain-specific knowledge and routing logic, enabling the STIHL Analytics Agent to intelligently route queries to appropriate tools and provide contextually relevant responses.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                                │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    SKILL ROUTER                          │    │
│  │  1. Check all skills for pattern matches                 │    │
│  │  2. Calculate confidence scores                          │    │
│  │  3. Select best match (confidence × priority)            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│  ┌──────────┬──────────┬──────────┬──────────┐                  │
│  │ Product  │  Sales   │Inventory │ Insights │                  │
│  │  Skill   │  Skill   │  Skill   │  Skill   │                  │
│  │  (RAG)   │  (SQL)   │  (SQL)   │  (SQL)   │                  │
│  │Priority:20│Priority:15│Priority:15│Priority:25│                │
│  └──────────┴──────────┴──────────┴──────────┘                  │
│                            ↓                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              ENHANCED SYSTEM PROMPT                      │    │
│  │  Base prompt + Skill-specific guidance + Available tools │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            ↓                                     │
│                    TOOL EXECUTION                                │
└─────────────────────────────────────────────────────────────────┘
```

## Available Skills

### 1. Product Expert (RAG)

| Property | Value |
|----------|-------|
| **Name** | `product_expert` |
| **Type** | RAG (Vector Search) |
| **Priority** | 20 |
| **Backend** | Databricks Vector Search |

**Handles:**
- Product recommendations based on use case
- Feature-based product search
- Product comparisons (MS 500i vs MS 462)
- Finding products by characteristics (lightweight, professional)

**Tools:** `search_products`, `compare_products`, `get_product_recommendations`

**Trigger Examples:**
- "What chainsaw is best for professional logging?"
- "Recommend a lightweight battery trimmer"
- "Compare the MS 500i and MS 462"
- "Products with anti-vibration feature"

---

### 2. Sales Analyst (SQL)

| Property | Value |
|----------|-------|
| **Name** | `sales_analyst` |
| **Type** | SQL |
| **Priority** | 15 |
| **Backend** | Databricks SQL Warehouse |

**Handles:**
- Revenue and sales volume analysis
- Top products/dealers/regions rankings
- Sales trends over time
- Category and regional breakdowns

**Tools:** `query_sales_data`

**Trigger Examples:**
- "What's our total revenue for 2024?"
- "Top selling products last quarter"
- "Sales trend month over month"
- "Revenue by region"

---

### 3. Inventory Analyst (SQL)

| Property | Value |
|----------|-------|
| **Name** | `inventory_analyst` |
| **Type** | SQL |
| **Priority** | 15 |
| **Backend** | Databricks SQL Warehouse |

**Handles:**
- Stock levels and availability
- Stockout identification
- Days of supply analysis
- Regional/category inventory distribution

**Tools:** `query_inventory_data`

**Trigger Examples:**
- "Current stock levels"
- "Products running low"
- "Stockouts in Southwest region"
- "Days of supply by category"

---

### 4. Insights Advisor (SQL)

| Property | Value |
|----------|-------|
| **Name** | `insights_advisor` |
| **Type** | SQL |
| **Priority** | 25 (Highest) |
| **Backend** | Databricks SQL Warehouse |

**Handles:**
- Morning greetings and daily briefings
- Proactive insights and alerts
- Anomaly detection
- What needs attention queries

**Tools:** `get_proactive_insights`, `detect_anomalies_realtime`, `get_daily_briefing`

**Trigger Examples:**
- "Good morning!"
- "What should I know today?"
- "Any anomalies in March 2024?"
- "Critical issues?"

---

## Routing Logic

### Pattern Matching

Each skill defines regex patterns that trigger activation:

```python
class ProductSkill(BaseSkill):
    @property
    def triggers(self) -> list[str]:
        return [
            r"(best|recommend|suggest).*(chainsaw|trimmer|blower)",
            r"(compare|vs|versus).*(ms|fs|bg)",
            # ... more patterns
        ]
```

### Confidence Scoring

Confidence is calculated based on:
1. **Pattern length** - Longer patterns = more specific = higher confidence
2. **Keyword overlap** - More matching keywords = higher confidence
3. **Base confidence** - All matches start at 0.7

### Selection Algorithm

```python
# Pseudo-code
matches = [skill.matches(query) for skill in skills]
matches.sort(key=lambda m: (m.confidence, skill.priority), reverse=True)
return matches[0]  # Best match
```

## File Structure

```
agent/skills/
├── __init__.py           # Package exports
├── base_skill.py         # BaseSkill abstract class
├── router.py             # SkillRouter implementation
├── product_skill.py      # RAG-based product search
├── sales_skill.py        # SQL-based sales analytics
├── inventory_skill.py    # SQL-based inventory analytics
├── insights_skill.py     # SQL-based proactive insights
└── SKILLS.md            # This documentation
```

## Usage Examples

### Basic Routing

```python
from agent.skills import route_query, get_router

# Simple routing
match = route_query("What chainsaw is best for professionals?")
print(match.skill_name)        # "product_expert"
print(match.confidence)        # 0.8
print(match.tools_available)   # ["search_products", "compare_products", ...]

# Get enhanced prompt
router = get_router()
skill = router.get_skill(match.skill_name)
enhanced = skill.get_enhanced_prompt(base_system_prompt)
```

### Debug Routing

```python
router = get_router()
explanation = router.explain_routing("Compare MS 500i and MS 462")
print(explanation)
# Query: Compare MS 500i and MS 462
#
# Matches found:
#   • product_expert: 0.85 confidence
#     Pattern: (compare|vs|versus).*(ms|fs|bg)
#     Tools: search_products, compare_products, get_product_recommendations
#
# ✅ Selected: product_expert
```

### List All Skills

```python
router = get_router()
for skill_info in router.list_skills():
    print(f"{skill_info['name']}: {skill_info['description']}")
```

## Adding New Skills

1. **Create skill file** in `agent/skills/`:

```python
# agent/skills/dealer_skill.py
from .base_skill import BaseSkill

class DealerSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "dealer_expert"
    
    @property
    def description(self) -> str:
        return "Analyze dealer performance and network"
    
    @property
    def triggers(self) -> list[str]:
        return [
            r"(dealer|distributor|partner)",
            r"(store|location|where to buy)",
        ]
    
    @property
    def tools(self) -> list[str]:
        return ["query_dealer_data"]
    
    @property
    def system_prompt(self) -> str:
        return "You are a STIHL dealer network expert..."
```

2. **Register in router.py**:

```python
from .dealer_skill import DealerSkill

def _register_default_skills(self):
    # ... existing skills
    self.register(DealerSkill())
```

3. **Export in __init__.py**:

```python
from .dealer_skill import DealerSkill
__all__ = [..., "DealerSkill"]
```

## Testing

```bash
# Run skill router tests
python -m tests.test_skills

# Test specific routing
python -c "
from agent.skills import get_router
router = get_router()
print(router.explain_routing('What chainsaw for professionals?'))
"
```

## Related Documentation

- [AGENT.md](../AGENT.md) - Agent architecture overview
- [tools/README.md](../tools/README.md) - Tool implementations
- [PROJECT_SUMMARY.md](../../PROJECT_SUMMARY.md) - Project overview
