"""
Test Databricks SQL Warehouse connection.
Run this first to verify your setup.

Usage: python -m tests.test_databricks_connection
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from databricks import sql


def test_connection():
    """Test Databricks connectivity and verify tables."""

    host = os.environ.get("DATABRICKS_HOST")
    http_path = os.environ.get("DATABRICKS_HTTP_PATH")
    token = os.environ.get("DATABRICKS_TOKEN")
    catalog = os.environ.get("DATABRICKS_CATALOG", "dbw_stihl_analytics")

    print("=" * 60)
    print("🔍 Testing Databricks SQL Warehouse Connection")
    print("=" * 60)
    print(f"\nHost: {host}")
    print(f"HTTP Path: {http_path}")
    print(f"Catalog: {catalog}")

    if not all([host, http_path, token]):
        print("\n❌ Missing environment variables. Check your .env file.")
        return False

    try:
        print("\n⏳ Connecting (may take 10-30s if warehouse is starting)...")

        connection = sql.connect(
            server_hostname=host,
            http_path=http_path,
            access_token=token,
        )
        cursor = connection.cursor()

        # Test 1: Basic query
        print("\n✅ Connected!")
        cursor.execute("SELECT 1 as test")
        print(f"   Basic query: {cursor.fetchone()}")

        # Test 2: Check catalog
        print(f"\n🔍 Checking catalog '{catalog}'...")
        cursor.execute(f"USE CATALOG {catalog}")
        print(f"   ✅ Catalog accessible")

        # Test 3: List schemas
        print(f"\n🔍 Listing schemas...")
        cursor.execute(f"SHOW SCHEMAS IN {catalog}")
        for schema in cursor.fetchall():
            print(f"   📁 {schema[0]}")

        # Test 4: Check gold tables
        print(f"\n🔍 Checking gold layer tables...")
        cursor.execute(f"SHOW TABLES IN {catalog}.gold")
        tables = [t[1] for t in cursor.fetchall()]
        for table in tables:
            print(f"   📊 {table}")

        # Test 5: Sample monthly_sales (using correct column names)
        print(f"\n🔍 Sampling monthly_sales...")
        cursor.execute(f"""
            SELECT year, month, SUM(total_revenue) as revenue
            FROM {catalog}.gold.monthly_sales
            GROUP BY year, month
            ORDER BY year DESC, month DESC
            LIMIT 5
        """)
        print("   Recent months:")
        for row in cursor.fetchall():
            print(f"   {row[0]}-{row[1]:02d}: ${row[2]:,.0f}")

        # Test 6: Check inventory status
        print(f"\n🔍 Checking inventory_status...")
        cursor.execute(f"""
            SELECT status, COUNT(*) as count
            FROM {catalog}.gold.inventory_status
            GROUP BY status
            ORDER BY count DESC
        """)
        print("   Inventory by status:")
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]} items")

        # Test 7: Check for Hurricane TX anomaly (Jun 2024, Southwest)
        print(f"\n🔍 Checking Hurricane TX anomaly (Jun 2024, Southwest)...")
        cursor.execute(f"""
            SELECT category, SUM(total_revenue) as revenue
            FROM {catalog}.gold.monthly_sales
            WHERE year = 2024 AND month = 6 AND region = 'Southwest'
            GROUP BY category
            ORDER BY revenue DESC
            LIMIT 3
        """)
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(f"   {row[0]}: ${row[1]:,.0f}")
        else:
            print("   ⚠️ No data found for June 2024 Southwest")

        # Test 8: Check for stockouts
        print(f"\n🔍 Checking for stockouts...")
        cursor.execute(f"""
            SELECT product_name, category, region
            FROM {catalog}.gold.inventory_status
            WHERE quantity_on_hand = 0
            LIMIT 5
        """)
        rows = cursor.fetchall()
        if rows:
            print(f"   Found {len(rows)} stockouts:")
            for row in rows:
                print(f"   - {row[0]} ({row[1]}) in {row[2]}")
        else:
            print("   ✅ No stockouts found")

        cursor.close()
        connection.close()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Is the SQL Warehouse running? Check Databricks UI")
        print("2. Is the token valid? Try regenerating it")
        print("3. Check .env file has correct values")
        return False


if __name__ == "__main__":
    test_connection()
