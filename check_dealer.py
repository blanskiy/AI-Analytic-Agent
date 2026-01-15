"""Quick diagnostic for dealer_performance table."""
from agent.databricks_client import DatabricksClient

client = DatabricksClient()

# Check columns
print("Columns:")
result = client.execute_query('DESCRIBE dbw_stihl_analytics.gold.dealer_performance')
for row in result['data']:
    print(f"  {row['col_name']}: {row['data_type']}")

# Check row count
result = client.execute_query('SELECT COUNT(*) as cnt FROM dbw_stihl_analytics.gold.dealer_performance')
print(f"\nRow count: {result['data'][0]['cnt']}")

# Sample data
result = client.execute_query('SELECT * FROM dbw_stihl_analytics.gold.dealer_performance LIMIT 3')
print(f"\nSample data:")
for row in result['data']:
    print(row)
