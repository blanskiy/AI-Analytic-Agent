"""
Inventory Skill - SQL-based inventory analytics.

Handles questions about:
- Stock levels and availability
- Stockouts and low stock alerts
- Days of supply analysis
- Regional/category inventory distribution

Uses: Databricks SQL Warehouse querying gold.inventory_status
"""
from .base_skill import BaseSkill


class InventorySkill(BaseSkill):
    """
    Inventory analytics skill using SQL queries.
    
    Routes to Databricks SQL for stock levels, stockout analysis,
    days of supply, and inventory health metrics.
    """
    
    @property
    def name(self) -> str:
        return "inventory_analyst"
    
    @property
    def description(self) -> str:
        return "Analyze inventory levels including stock status, stockouts, and days of supply"
    
    @property
    def triggers(self) -> list[str]:
        return [
            # Stock level patterns
            r"(stock|inventory)\s+.*(level|status|available|on.hand)",
            r"(how much|what|current)\s+.*(stock|inventory)",
            r"(in stock|out of stock|available)",
            
            # Stockout patterns
            r"(stockout|stock.?out|zero.stock|no.stock|out.of)",
            r"(running|ran)\s+(low|out)",
            r"(shortage|depleted|exhausted)",
            
            # Days of supply patterns
            r"(days|weeks)\s+(of|worth).*(supply|stock|inventory)",
            r"(how long|when).*(last|run.out|deplete)",
            r"(supply|coverage).*(day|week)",
            
            # Status patterns
            r"(critical|low|normal)\s+.*(stock|inventory|status)",
            r"(at.?risk|warning|alert).*(inventory|stock)",
            r"(reorder|replenish|refill)",
            
            # Distribution patterns
            r"(inventory|stock)\s+.*(by|per|each)\s+(region|category|warehouse|product)",
            r"(warehouse|distribution|regional)\s+.*(stock|inventory)",
            
            # Health patterns
            r"(inventory|stock)\s+.*(health|status|overview|summary)",
            r"(overstock|excess|surplus)",
        ]
    
    @property
    def tools(self) -> list[str]:
        return ["query_inventory_data"]
    
    @property
    def system_prompt(self) -> str:
        return """You are a STIHL inventory analyst monitoring stock health.

## Your Approach
1. **Assess urgency** - Identify critical issues first
2. **Provide actionable data** - Include quantities and timeframes
3. **Prioritize** - Help focus attention on what matters most

## Stock Status Levels
- **CRITICAL**: Days of supply < 7 - Immediate action needed
- **LOW**: Days of supply 7-14 - Monitor closely, consider reorder
- **NORMAL**: Days of supply > 14 - Healthy stock levels

## Query Types
- `summary`: Overall inventory metrics
- `low_stock`: Products with low days of supply
- `stockouts`: Products with zero inventory
- `by_category`: Inventory by product category
- `by_region`: Regional inventory distribution
- `days_of_supply`: Sorted by days of supply

## Response Guidelines
- Lead with critical issues if any exist
- Include specific product names and quantities
- Recommend actions for low stock situations
- Compare to normal levels when helpful
- Flag patterns (e.g., "all battery products low in Southwest")"""
    
    @property
    def priority(self) -> int:
        return 15  # Standard priority
