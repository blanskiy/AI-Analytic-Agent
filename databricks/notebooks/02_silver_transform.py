# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver Layer Transform
# MAGIC Clean and type-cast data from Bronze to Silver

# COMMAND ----------

# Cell 1: Configuration
catalog = "dbw_stihl_analytics"
bronze_schema = "bronze"
silver_schema = "silver"

spark.sql(f"USE CATALOG {catalog}")

# COMMAND ----------

# Cell 2: Products - Clean and type cast
from pyspark.sql.functions import col

products_bronze = spark.table(f"{bronze_schema}.products")

products_silver = products_bronze.select(
    col("product_id"),
    col("product_name"),
    col("category"),
    col("subcategory"),
    col("product_line"),
    col("power_type"),
    col("engine_cc").cast("double"),
    col("voltage").cast("int"),
    col("weight_lbs").cast("double"),
    col("msrp").cast("double"),
    col("cost").cast("double"),
    col("description"),
    col("features"),
    col("is_active").cast("boolean")
)

products_silver.write.mode("overwrite").saveAsTable(f"{silver_schema}.products")
print(f"✅ Silver products: {products_silver.count()} rows")

# COMMAND ----------

# Cell 3: Sales - Clean and type cast
from pyspark.sql.functions import to_date

sales_bronze = spark.table(f"{bronze_schema}.sales")

sales_silver = sales_bronze.select(
    col("transaction_id"),
    to_date(col("transaction_date")).alias("transaction_date"),
    col("product_id"),
    col("product_name"),
    col("category"),
    col("dealer_id"),
    col("dealer_name"),
    col("region"),
    col("state"),
    col("quantity").cast("int"),
    col("unit_price").cast("double"),
    col("discount_pct").cast("double"),
    col("total_amount").cast("double"),
    col("customer_type"),
    col("channel")
)

sales_silver.write.mode("overwrite").saveAsTable(f"{silver_schema}.sales")
print(f"✅ Silver sales: {sales_silver.count():,} rows")

# COMMAND ----------

# Cell 4: Inventory - Clean and type cast
inventory_bronze = spark.table(f"{bronze_schema}.inventory")

inventory_silver = inventory_bronze.select(
    to_date(col("snapshot_date")).alias("snapshot_date"),
    col("product_id"),
    col("product_name"),
    col("category"),
    col("warehouse_id"),
    col("region"),
    col("quantity_on_hand").cast("int"),
    col("quantity_available").cast("int"),
    col("quantity_reserved").cast("int"),
    col("reorder_point").cast("int"),
    col("days_of_supply").cast("double"),
    col("status")
)

inventory_silver.write.mode("overwrite").saveAsTable(f"{silver_schema}.inventory")
print(f"✅ Silver inventory: {inventory_silver.count():,} rows")

# COMMAND ----------

# Cell 5: Dealers - Clean and type cast
dealers_bronze = spark.table(f"{bronze_schema}.dealers")

dealers_silver = dealers_bronze.select(
    col("dealer_id"),
    col("dealer_name"),
    col("city"),
    col("state"),
    col("region"),
    col("dealer_type"),
    col("year_established").cast("int"),
    col("is_active").cast("boolean")
)

dealers_silver.write.mode("overwrite").saveAsTable(f"{silver_schema}.dealers")
print(f"✅ Silver dealers: {dealers_silver.count()} rows")

# COMMAND ----------

# Cell 6: Verify silver tables
spark.sql(f"SHOW TABLES IN {silver_schema}").show()
