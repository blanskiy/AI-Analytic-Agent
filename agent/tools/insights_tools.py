"""
Proactive Insights tools for STIHL Analytics Agent.
Updated to match actual Databricks schema.
"""

import json
from typing import Optional
from datetime import datetime

from agent.databricks_client import execute_query
from config.settings import get_config


def get_proactive_insights(
    insight_types: Optional[list[str]] = None,
    severity_filter: Optional[str] = None,
    max_insights: int = 5
) -> str:
    """
    Retrieve proactive insights - anomalies, alerts, and trends worth attention.

    IMPORTANT: Call this at the START of conversations when the user asks
    general questions like "What should I know?" or "Any updates?" or just "Hi".

    Args:
        insight_types: Filter by type (anomaly, stockout_risk, trend, forecast_alert, opportunity)
        severity_filter: Filter by urgency (critical, warning, info)
        max_insights: Maximum insights to return (default 5)

    Returns:
        JSON with prioritized insights
    """
    config = get_config()
    catalog = config.databricks.catalog
    
    # Check if proactive_insights table exists, if not generate insights on-the-fly
    try:
        insights_table = f"{catalog}.gold.proactive_insights"
        
        filters = ["is_active = true"]
        if insight_types:
            types_str = ", ".join([f"'{t}'" for t in insight_types])
            filters.append(f"insight_type IN ({types_str})")
        if severity_filter:
            filters.append(f"severity = '{severity_filter}'")
        filter_clause = " AND ".join(filters)

        query = f"""
        SELECT 
            insight_id, insight_type, severity, title, description,
            affected_entity, metric_name, metric_value, expected_value,
            deviation_pct, detected_at, recommended_action
        FROM {insights_table}
        WHERE {filter_clause}
        ORDER BY 
            CASE severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END,
            ABS(deviation_pct) DESC
        LIMIT {max_insights}
        """

        result = execute_query(query)
        
        if result.get("success") and result.get("data"):
            result["narrative_summary"] = _format_insights_narrative(result["data"])
            return json.dumps(result, default=str)
    except:
        pass
    
    # Fallback: Generate insights from current data
    return _generate_realtime_insights(max_insights)


def _generate_realtime_insights(max_insights: int = 5) -> str:
    """Generate insights on-the-fly from current data."""
    config = get_config()
    catalog = config.databricks.catalog
    
    insights = []
    
    # Check for stockouts
    stockout_query = f"""
    SELECT product_name, category, region, COUNT(*) as locations
    FROM {catalog}.gold.inventory_status
    WHERE quantity_on_hand = 0
    GROUP BY product_name, category, region
    ORDER BY locations DESC
    LIMIT 3
    """
    stockout_result = execute_query(stockout_query)
    if stockout_result.get("success") and stockout_result.get("data"):
        for row in stockout_result["data"]:
            insights.append({
                "insight_type": "stockout_risk",
                "severity": "critical",
                "title": f"STOCKOUT: {row['product_name']}",
                "description": f"{row['product_name']} is out of stock in {row['region']}",
                "affected_entity": row["product_name"],
                "recommended_action": f"Reorder {row['product_name']} immediately"
            })
    
    # Check for critical inventory
    critical_query = f"""
    SELECT product_name, category, region, days_of_supply, quantity_on_hand
    FROM {catalog}.gold.inventory_status
    WHERE status = 'Critical' AND quantity_on_hand > 0
    ORDER BY days_of_supply ASC
    LIMIT 3
    """
    critical_result = execute_query(critical_query)
    if critical_result.get("success") and critical_result.get("data"):
        for row in critical_result["data"]:
            insights.append({
                "insight_type": "stockout_risk",
                "severity": "warning",
                "title": f"Critical Stock: {row['product_name']}",
                "description": f"{row['product_name']} has only {row['days_of_supply']:.0f} days of supply in {row['region']}",
                "affected_entity": row["product_name"],
                "metric_value": row["days_of_supply"],
                "recommended_action": f"Review reorder for {row['product_name']}"
            })
    
    # Check for sales anomalies (high performers)
    sales_query = f"""
    SELECT category, region, SUM(total_revenue) as revenue, SUM(total_units) as units
    FROM {catalog}.gold.monthly_sales
    WHERE year = 2024 AND month = 6
    GROUP BY category, region
    ORDER BY revenue DESC
    LIMIT 2
    """
    sales_result = execute_query(sales_query)
    if sales_result.get("success") and sales_result.get("data"):
        for row in sales_result["data"]:
            insights.append({
                "insight_type": "opportunity",
                "severity": "info",
                "title": f"Strong Sales: {row['category']} in {row['region']}",
                "description": f"{row['category']} generated ${row['revenue']:,.0f} in {row['region']}",
                "affected_entity": row["category"],
                "metric_value": row["revenue"],
                "recommended_action": "Consider increasing inventory for this category"
            })
    
    # Limit and format
    insights = insights[:max_insights]
    
    return json.dumps({
        "success": True,
        "row_count": len(insights),
        "data": insights,
        "narrative_summary": _format_insights_narrative(insights),
        "source": "realtime_analysis"
    }, default=str)


def _format_insights_narrative(insights: list[dict]) -> str:
    """Convert insights to natural language summary."""
    if not insights:
        return "No significant insights requiring attention at this time."

    narratives = []
    for insight in insights:
        emoji = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(insight.get("severity", "info"), "ℹ️")
        narratives.append(f"{emoji} **{insight.get('title', 'Insight')}**: {insight.get('description', '')}")

    return "\n".join(narratives)


def detect_anomalies_realtime(
    metric: str,
    entity_type: str,
    threshold_std: float = 2.0
) -> str:
    """
    Run real-time anomaly detection on specified metrics.

    Args:
        metric: Metric to analyze (revenue, units_sold, stock_level)
        entity_type: Grouping dimension (category, region)
        threshold_std: Standard deviations for anomaly (default 2.0)

    Returns:
        JSON with detected anomalies ranked by deviation
    """
    config = get_config()
    catalog = config.databricks.catalog

    metric_config = {
        "revenue": {
            "table": f"{catalog}.gold.monthly_sales",
            "column": "total_revenue",
            "group_col": "category" if entity_type == "category" else "region"
        },
        "units_sold": {
            "table": f"{catalog}.gold.monthly_sales",
            "column": "total_units",
            "group_col": "category" if entity_type == "category" else "region"
        },
        "stock_level": {
            "table": f"{catalog}.gold.inventory_status",
            "column": "quantity_on_hand",
            "group_col": "category" if entity_type == "category" else "region"
        }
    }

    if metric not in metric_config:
        return json.dumps({
            "success": False,
            "error": f"Unknown metric: {metric}. Use: {', '.join(metric_config.keys())}"
        })

    mc = metric_config[metric]

    query = f"""
    WITH baseline AS (
        SELECT 
            {mc['group_col']} as entity,
            AVG({mc['column']}) as mean_value,
            STDDEV({mc['column']}) as std_value
        FROM {mc['table']}
        GROUP BY {mc['group_col']}
    ),
    current_values AS (
        SELECT 
            {mc['group_col']} as entity,
            SUM({mc['column']}) as current_value
        FROM {mc['table']}
        GROUP BY {mc['group_col']}
    )
    SELECT 
        c.entity,
        c.current_value,
        b.mean_value as expected_value,
        ROUND((c.current_value - b.mean_value) / NULLIF(b.std_value, 0), 2) as z_score,
        ROUND((c.current_value - b.mean_value) / NULLIF(b.mean_value, 0) * 100, 1) as pct_deviation,
        CASE 
            WHEN ABS((c.current_value - b.mean_value) / NULLIF(b.std_value, 0)) > {threshold_std * 1.5} THEN 'critical'
            WHEN ABS((c.current_value - b.mean_value) / NULLIF(b.std_value, 0)) > {threshold_std} THEN 'warning'
            ELSE 'normal'
        END as anomaly_status
    FROM current_values c
    JOIN baseline b ON c.entity = b.entity
    WHERE b.std_value > 0 AND ABS((c.current_value - b.mean_value) / NULLIF(b.std_value, 0)) > {threshold_std}
    ORDER BY ABS((c.current_value - b.mean_value) / NULLIF(b.std_value, 0)) DESC
    LIMIT 10
    """

    result = execute_query(query)
    result["metric_analyzed"] = metric
    result["entity_type"] = entity_type
    result["threshold_std"] = threshold_std
    return json.dumps(result, default=str)


def get_daily_briefing() -> str:
    """
    Generate comprehensive daily briefing for the user.
    Call when user starts conversation or asks for overview.

    Returns:
        JSON with structured daily briefing
    """
    config = get_config()
    catalog = config.databricks.catalog

    # Get key metrics
    metrics_query = f"""
    SELECT 'total_revenue' as metric, SUM(total_revenue) as value
    FROM {catalog}.gold.monthly_sales
    UNION ALL
    SELECT 'stockouts' as metric, COUNT(*) as value
    FROM {catalog}.gold.inventory_status WHERE quantity_on_hand = 0
    UNION ALL
    SELECT 'critical_stock' as metric, COUNT(*) as value
    FROM {catalog}.gold.inventory_status WHERE status = 'Critical' AND quantity_on_hand > 0
    UNION ALL
    SELECT 'low_stock' as metric, COUNT(*) as value
    FROM {catalog}.gold.inventory_status WHERE status = 'Low'
    """

    metrics_result = execute_query(metrics_query)
    insights_result = json.loads(get_proactive_insights(max_insights=3))

    briefing = {
        "generated_at": datetime.now().isoformat(),
        "key_metrics": metrics_result.get("data", []),
        "top_insights": insights_result.get("data", []),
        "narrative": _generate_briefing_narrative(
            metrics_result.get("data", []),
            insights_result.get("data", [])
        )
    }
    return json.dumps(briefing, default=str)


def _generate_briefing_narrative(metrics: list, insights: list) -> str:
    """Generate natural language briefing."""
    parts = ["**Daily Briefing**\n"]

    metrics_dict = {m.get("metric"): m.get("value", 0) for m in metrics}
    
    if metrics_dict.get("stockouts", 0) > 0:
        parts.append(f"⚠️ {int(metrics_dict['stockouts'])} products currently out of stock")
    if metrics_dict.get("critical_stock", 0) > 0:
        parts.append(f"🔴 {int(metrics_dict['critical_stock'])} products with critical inventory")
    if metrics_dict.get("low_stock", 0) > 0:
        parts.append(f"🟡 {int(metrics_dict['low_stock'])} products with low inventory")
    if metrics_dict.get("total_revenue", 0) > 0:
        parts.append(f"💰 Total revenue: ${metrics_dict['total_revenue']:,.0f}")

    if insights:
        parts.append(f"\n**Top Priority:** {insights[0].get('title', 'No urgent items')}")

    return "\n".join(parts)


# Tool definitions for Azure AI Foundry
PROACTIVE_INSIGHTS_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_proactive_insights",
        "description": "Get proactive insights - anomalies, alerts, and trends. Call at conversation START.",
        "parameters": {
            "type": "object",
            "properties": {
                "insight_types": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["anomaly", "stockout_risk", "trend", "forecast_alert", "opportunity"]}
                },
                "severity_filter": {"type": "string", "enum": ["critical", "warning", "info"]},
                "max_insights": {"type": "integer"}
            }
        }
    }
}

DETECT_ANOMALIES_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "detect_anomalies_realtime",
        "description": "Run real-time anomaly detection on specified metrics.",
        "parameters": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "enum": ["revenue", "units_sold", "stock_level"]},
                "entity_type": {"type": "string", "enum": ["category", "region"]},
                "threshold_std": {"type": "number"}
            },
            "required": ["metric", "entity_type"]
        }
    }
}

DAILY_BRIEFING_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_daily_briefing",
        "description": "Generate comprehensive daily briefing with key metrics and insights.",
        "parameters": {"type": "object", "properties": {}}
    }
}
