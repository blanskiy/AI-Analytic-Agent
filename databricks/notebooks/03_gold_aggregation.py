# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold Layer Aggregation
# MAGIC Create analytics-ready aggregated tables

# COMMAND ----------

# Cell 1: Configuration
catalog = "dbw_stihl_analytics"
silver_schema = "silver"
gold_schema = "gold"

spark.sql(f"USE CATALOG {catalog}")

# COMMAND ----------

# Cell 2: Monthly Sales by Category and Region
from pyspark.sql.functions import year, month, sum, count, avg, round, col

sales = spark.table(f"{silver_schema}.sales")

monthly_sales = sales.groupBy(
    year("transaction_date").alias("year"),
    month("transaction_date").alias("month"),
    "category",
    "region"
).agg(
    count("*").alias("transaction_count"),
    sum("quantity").alias("total_units"),
    round(sum("total_amount"), 2).alias("total_revenue"),
    round(avg("total_amount"), 2).alias("avg_transaction_value")
).orderBy("year", "month", "category", "region")

monthly_sales.write.mode("overwrite").saveAsTable(f"{gold_schema}.monthly_sales")
print(f"✅ Gold monthly_sales: {monthly_sales.count():,} rows")
monthly_sales.show(10)

# COMMAND ----------

# Cell 3: Product Performance Summary
product_performance = sales.groupBy(
    "product_id",
    "product_name",
    "category"
).agg(
    count("*").alias("transaction_count"),
    sum("quantity").alias("total_units_sold"),
    round(sum("total_amount"), 2).alias("total_revenue"),
    round(avg("discount_pct"), 2).alias("avg_discount_pct")
).orderBy("total_revenue", ascending=False)

product_performance.write.mode("overwrite").saveAsTable(f"{gold_schema}.product_performance")
print(f"✅ Gold product_performance: {product_performance.count()} rows")
product_performance.show(10)

# COMMAND ----------

# Cell 4: Dealer Performance Summary
dealer_performance = sales.groupBy(
    "dealer_id",
    "dealer_name",
    "region",
    "state"
).agg(
    count("*").alias("transaction_count"),
    sum("quantity").alias("total_units_sold"),
    round(sum("total_amount"), 2).alias("total_revenue")
).orderBy("total_revenue", ascending=False)

dealer_performance.write.mode("overwrite").saveAsTable(f"{gold_schema}.dealer_performance")
print(f"✅ Gold dealer_performance: {dealer_performance.count()} rows")
dealer_performance.show(10)

# COMMAND ----------

# Cell 5: Latest Inventory Status
from pyspark.sql.functions import max

inventory = spark.table(f"{silver_schema}.inventory")

# Get latest snapshot date
latest_date = inventory.agg(max("snapshot_date")).collect()[0][0]

inventory_status = inventory.filter(col("snapshot_date") == latest_date).select(
    "product_id",
    "product_name",
    "category",
    "warehouse_id",
    "region",
    "quantity_on_hand",
    "quantity_available",
    "days_of_supply",
    "status"
)

inventory_status.write.mode("overwrite").saveAsTable(f"{gold_schema}.inventory_status")
print(f"✅ Gold inventory_status: {inventory_status.count():,} rows (as of {latest_date})")
inventory_status.show(10)

# COMMAND ----------

# Cell 6: Verify all gold tables
spark.sql(f"SHOW TABLES IN {gold_schema}").show()

print("\n📊 Medallion Architecture Complete!")
print(f"   Bronze: 4 tables (raw)")
print(f"   Silver: 4 tables (cleaned)")
print(f"   Gold: 4 tables (aggregated)")
