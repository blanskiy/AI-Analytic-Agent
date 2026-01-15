# Databricks notebook source
# MAGIC %md
# MAGIC # STIHL Analytics - Proactive Insights Pipeline
# MAGIC 
# MAGIC Generates the `gold.proactive_insights` table used by the AI agent.
# MAGIC Schedule to run daily via Databricks Workflows.
# MAGIC 
# MAGIC **Output**: `dbw_stihl_analytics.gold.proactive_insights`

# COMMAND ----------

CATALOG = "dbw_stihl_analytics"
SCHEMA_GOLD = "gold"

ANOMALY_THRESHOLD_STD = 2.0
CRITICAL_DOS_THRESHOLD = 7
LOW_DOS_THRESHOLD = 14

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create Proactive Insights Table

# COMMAND ----------

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA_GOLD}.proactive_insights (
    insight_id STRING,
    insight_type STRING,
    severity STRING,
    title STRING,
    description STRING,
    affected_entity STRING,
    affected_entity_type STRING,
    metric_name STRING,
    metric_value DOUBLE,
    expected_value DOUBLE,
    deviation_pct DOUBLE,
    detected_at TIMESTAMP,
    is_active BOOLEAN,
    recommended_action STRING,
    supporting_data STRING
)
USING DELTA
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Detect Sales Anomalies
# MAGIC 
# MAGIC Using actual schema: year, month, category, region, total_revenue, total_units

# COMMAND ----------

from pyspark.sql import functions as F
import uuid

def generate_id():
    return str(uuid.uuid4())[:8]

# Note: Using actual column names from your schema
sales_anomalies_df = spark.sql(f"""
WITH monthly_stats AS (
    SELECT 
        category, region, year, month,
        total_revenue, total_units,
        AVG(total_revenue) OVER (
            PARTITION BY category, region 
            ORDER BY year, month 
            ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
        ) as avg_revenue,
        STDDEV(total_revenue) OVER (
            PARTITION BY category, region 
            ORDER BY year, month 
            ROWS BETWEEN 6 PRECEDING AND 1 PRECEDING
        ) as std_revenue
    FROM {CATALOG}.{SCHEMA_GOLD}.monthly_sales
),
anomalies AS (
    SELECT *,
        (total_revenue - avg_revenue) / NULLIF(std_revenue, 0) as z_score,
        (total_revenue - avg_revenue) / NULLIF(avg_revenue, 0) * 100 as pct_deviation
    FROM monthly_stats
    WHERE std_revenue > 0
)
SELECT 
    category, region, year, month,
    total_revenue as metric_value, avg_revenue as expected_value, z_score, pct_deviation,
    CASE 
        WHEN z_score > 3 THEN 'Extreme spike'
        WHEN z_score > {ANOMALY_THRESHOLD_STD} THEN 'Significant spike'
        WHEN z_score < -3 THEN 'Extreme drop'
        WHEN z_score < -{ANOMALY_THRESHOLD_STD} THEN 'Significant drop'
    END as anomaly_type
FROM anomalies
WHERE ABS(z_score) > {ANOMALY_THRESHOLD_STD}
ORDER BY ABS(z_score) DESC
LIMIT 20
""")

sales_insights = sales_anomalies_df.select(
    F.lit(generate_id()).alias("insight_id"),
    F.lit("anomaly").alias("insight_type"),
    F.when(F.abs(F.col("z_score")) > 3, "critical").otherwise("warning").alias("severity"),
    F.concat(F.col("anomaly_type"), F.lit(" in "), F.col("category"), F.lit(" ("), F.col("region"), F.lit(")")).alias("title"),
    F.concat(
        F.col("category"), F.lit(" sales in "), F.col("region"),
        F.lit(" for "), F.col("month"), F.lit("/"), F.col("year"),
        F.lit(" were "), F.round(F.col("pct_deviation"), 1), F.lit("% "),
        F.when(F.col("pct_deviation") > 0, "above").otherwise("below"),
        F.lit(" expected ($"), F.round(F.col("expected_value"), 0), F.lit(")")
    ).alias("description"),
    F.col("category").alias("affected_entity"),
    F.lit("category").alias("affected_entity_type"),
    F.lit("revenue").alias("metric_name"),
    F.col("metric_value"),
    F.col("expected_value"),
    F.col("pct_deviation").alias("deviation_pct"),
    F.current_timestamp().alias("detected_at"),
    F.lit(True).alias("is_active"),
    F.when(F.col("pct_deviation") > 100,
        F.concat(F.lit("Investigate demand surge for "), F.col("category"), F.lit(" in "), F.col("region"))
    ).otherwise(F.lit("Monitor this trend")).alias("recommended_action"),
    F.to_json(F.struct(F.col("category"), F.col("year"), F.col("month"))).alias("supporting_data")
)

print(f"Found {sales_anomalies_df.count()} sales anomalies")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Detect Inventory Alerts
# MAGIC 
# MAGIC Using actual schema: product_name, category, warehouse_id, region, quantity_on_hand, days_of_supply, status

# COMMAND ----------

# Note: Using actual column names from your schema
inventory_alerts_df = spark.sql(f"""
SELECT 
    product_name, category, warehouse_id, region,
    quantity_on_hand, quantity_available, days_of_supply, status
FROM {CATALOG}.{SCHEMA_GOLD}.inventory_status
WHERE quantity_on_hand = 0 OR status IN ('Critical', 'Low')
ORDER BY 
    CASE status 
        WHEN 'Critical' THEN 1 
        WHEN 'Low' THEN 2 
        ELSE 3 
    END,
    days_of_supply ASC
LIMIT 20
""")

inventory_insights = inventory_alerts_df.select(
    F.lit(generate_id()).alias("insight_id"),
    F.lit("stockout_risk").alias("insight_type"),
    F.when(F.col("quantity_on_hand") == 0, "critical")
     .when(F.col("status") == "Critical", "critical")
     .otherwise("warning").alias("severity"),
    F.concat(
        F.when(F.col("quantity_on_hand") == 0, F.lit("STOCKOUT: "))
         .when(F.col("status") == "Critical", F.lit("Critical: "))
         .otherwise(F.lit("Low Stock: ")),
        F.col("product_name"), F.lit(" in "), F.col("region")
    ).alias("title"),
    F.concat(
        F.col("product_name"), F.lit(" ("), F.col("category"), F.lit(") in "), F.col("region"),
        F.when(F.col("quantity_on_hand") == 0, F.lit(" has zero inventory"))
         .otherwise(F.concat(F.lit(" has "), F.round(F.col("days_of_supply"), 0), F.lit(" days supply")))
    ).alias("description"),
    F.col("product_name").alias("affected_entity"),
    F.lit("product").alias("affected_entity_type"),
    F.lit("days_of_supply").alias("metric_name"),
    F.col("days_of_supply").cast("double").alias("metric_value"),
    F.lit(30.0).alias("expected_value"),
    F.round((F.col("days_of_supply") - 30) / 30 * 100, 1).alias("deviation_pct"),
    F.current_timestamp().alias("detected_at"),
    F.lit(True).alias("is_active"),
    F.concat(F.lit("Reorder "), F.col("product_name"), F.lit(" immediately")).alias("recommended_action"),
    F.to_json(F.struct(F.col("category"), F.col("warehouse_id"), F.col("quantity_on_hand"))).alias("supporting_data")
)

print(f"Found {inventory_alerts_df.count()} inventory alerts")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Write Insights

# COMMAND ----------

# Deactivate old insights
spark.sql(f"""
UPDATE {CATALOG}.{SCHEMA_GOLD}.proactive_insights
SET is_active = false
WHERE is_active = true AND detected_at < current_timestamp() - INTERVAL 1 DAY
""")

# Combine and write
all_insights = sales_insights.union(inventory_insights)
all_insights.write.format("delta").mode("append").saveAsTable(f"{CATALOG}.{SCHEMA_GOLD}.proactive_insights")

print(f"✅ Generated {all_insights.count()} new insights")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Summary

# COMMAND ----------

display(spark.sql(f"""
SELECT insight_type, severity, COUNT(*) as count
FROM {CATALOG}.{SCHEMA_GOLD}.proactive_insights
WHERE is_active = true
GROUP BY insight_type, severity
ORDER BY 
    CASE severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END
"""))

# COMMAND ----------

# Show sample insights
display(spark.sql(f"""
SELECT title, severity, description, recommended_action
FROM {CATALOG}.{SCHEMA_GOLD}.proactive_insights
WHERE is_active = true
ORDER BY 
    CASE severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END
LIMIT 10
"""))
