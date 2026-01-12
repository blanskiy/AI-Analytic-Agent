# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze Layer Ingestion
# MAGIC Load raw data from ADLS into Delta tables

# COMMAND ----------

# Cell 1: Configuration
catalog = "dbw_stihl_analytics"
bronze_schema = "bronze"
adls_path = "abfss://stihl-analytics-data@adlsstihlanalytics.dfs.core.windows.net/bronze"

# Set catalog context
spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA {bronze_schema}")

# List files in ADLS
files = dbutils.fs.ls(adls_path)
for f in files:
    print(f"{f.name} - {f.size / 1024:.1f} KB")

# COMMAND ----------

# Cell 2: Load Products from JSON
products_df = spark.read.option("multiLine", "true").json(f"{adls_path}/products_raw/products.json")

# Write to Delta table
products_df.write.mode("overwrite").saveAsTable("products")

print(f"✅ Loaded {products_df.count()} products")
products_df.show(5)

# COMMAND ----------

# Cell 3: Load Dealers from CSV
dealers_df = spark.read.option("header", "true").csv(f"{adls_path}/dealers_raw/")

# Write to Delta table
dealers_df.write.mode("overwrite").saveAsTable("dealers")

print(f"✅ Loaded {dealers_df.count()} dealers")
dealers_df.show(5)

# COMMAND ----------

# Cell 4: Load Sales from CSV files
sales_df = spark.read.option("header", "true").csv(f"{adls_path}/sales_raw/")

# Write to Delta table
sales_df.write.mode("overwrite").saveAsTable("sales")

print(f"✅ Loaded {sales_df.count():,} sales transactions")
sales_df.show(5)

# COMMAND ----------

# Cell 5: Load Inventory from CSV files
inventory_df = spark.read.option("header", "true").csv(f"{adls_path}/inventory_raw/")

# Write to Delta table
inventory_df.write.mode("overwrite").saveAsTable("inventory")

print(f"✅ Loaded {inventory_df.count():,} inventory snapshots")
inventory_df.show(5)

# COMMAND ----------

# Cell 6: Verify all tables created
spark.sql("SHOW TABLES").show()
