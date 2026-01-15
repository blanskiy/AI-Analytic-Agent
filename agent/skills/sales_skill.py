"""
Sales Skill - SQL-based sales analytics.

Handles questions about:
- Revenue and sales volume
- Top performing products/dealers/regions
- Sales trends over time
- Category and regional breakdowns

Uses: Databricks SQL Warehouse querying gold.monthly_sales, gold.product_performance
"""
from .base_skill import BaseSkill


class SalesSkill(BaseSkill):
    """
    Sales analytics skill using SQL queries.
    
    Routes to Databricks SQL for quantitative sales metrics,
    trends, rankings, and performance analysis.
    """
    
    @property
    def name(self) -> str:
        return "sales_analyst"
    
    @property
    def description(self) -> str:
        return "Analyze sales performance including revenue, trends, rankings, and regional breakdowns"
    
    @property
    def triggers(self) -> list[str]:
        return [
            # Revenue/sales patterns
            r"(revenue|sales|sold|selling)\s+.*(total|how much|summary|overview)",
            r"(total|overall|aggregate)\s+.*(revenue|sales|income)",
            r"(how much|what).*(revenue|sales|sold|made)",
            r"\$\s*\d+.*(revenue|sales)",
            
            # Performance/ranking patterns
            r"(top|best|worst|bottom|leading|highest|lowest)\s+.*(product|seller|dealer|region|category)",
            r"(best|top).*(selling|performer|revenue)",
            r"(rank|ranking|leaderboard)",
            
            # Trend patterns
            r"(trend|growth|decline|change|over time)",
            r"(month|quarter|year)\s*(over|to|vs)\s*(month|quarter|year)",
            r"(ytd|year.to.date|mtd|qtd)",
            r"(last|previous|this)\s+(month|quarter|year|week)",
            
            # Time period patterns
            r"(2024|2025|q1|q2|q3|q4|january|february|march|april|may|june|july|august|september|october|november|december)",
            r"(fiscal|financial)\s+(year|quarter|period)",
            
            # Breakdown patterns
            r"(by|per|each)\s+(region|category|dealer|product|month|quarter)",
            r"(breakdown|split|distribution|mix)\s+.*(sales|revenue)",
            r"(regional|category|dealer)\s+.*(performance|sales|revenue)",
            
            # Comparison patterns (sales context)
            r"(compare|comparison).*(sales|revenue|region|period)",
            r"(versus|vs)\s+.*(last|previous|prior)\s+(month|quarter|year)",
        ]
    
    @property
    def tools(self) -> list[str]:
        return ["query_sales_data"]
    
    @property
    def system_prompt(self) -> str:
        return """You are a STIHL sales analyst providing data-driven insights.

## Your Approach
1. **Query the right data** - Use appropriate time periods and filters
2. **Provide context** - Compare to benchmarks or prior periods when relevant
3. **Highlight insights** - Don't just report numbers, explain what they mean

## Data Available
- **Time Range**: January 2024 - December 2025 (24 months)
- **Metrics**: Revenue, units sold, transaction count, average price
- **Dimensions**: Product, category, region, dealer, month

## Query Types
- `summary`: Overall metrics for a period
- `top_products`: Best sellers by revenue
- `top_dealers`: Best performing dealers
- `trend`: Month-over-month trends
- `by_category`: Category breakdown
- `by_region`: Regional breakdown

## Response Guidelines
- Lead with the key metric they asked about
- Provide comparative context (vs prior period, vs other regions)
- Format large numbers clearly ($394.9M not $394927843)
- Offer drill-down suggestions when appropriate"""
    
    @property
    def priority(self) -> int:
        return 15  # Standard priority
