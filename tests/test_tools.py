"""
Test agent tools against Databricks.
Usage: python -m tests.test_tools
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from agent.tools.sales_tools import query_sales_data
from agent.tools.inventory_tools import query_inventory_data
from agent.tools.insights_tools import get_proactive_insights, get_daily_briefing


def test_sales_summary():
    print("=== Testing Sales Summary ===")
    result = json.loads(query_sales_data("summary"))
    print(f"Success: {result['success']}")
    if result["success"] and result["data"]:
        d = result["data"][0]
        print(f"  Total Revenue: ${d.get('total_revenue', 0):,.0f}")
        print(f"  Total Units: {d.get('total_units', 0):,}")
        print(f"  Periods: {d.get('periods', 0)}")
    else:
        print(f"  Error: {result.get('error', 'No data')}")
    return result["success"]


def test_top_products():
    print("\n=== Testing Top Products ===")
    result = json.loads(query_sales_data("top_products", top_n=5))
    print(f"Success: {result['success']}")
    if result["success"] and result["data"]:
        for p in result["data"][:5]:
            print(f"  {p['product_name']}: ${p['revenue']:,.0f}")
    else:
        print(f"  Error: {result.get('error', 'No data')}")
    return result["success"]


def test_sales_by_region():
    print("\n=== Testing Sales by Region ===")
    result = json.loads(query_sales_data("by_region"))
    print(f"Success: {result['success']}")
    if result["success"] and result["data"]:
        for r in result["data"]:
            print(f"  {r['region']}: ${r['revenue']:,.0f}")
    else:
        print(f"  Error: {result.get('error', 'No data')}")
    return result["success"]


def test_inventory_summary():
    print("\n=== Testing Inventory Summary ===")
    result = json.loads(query_inventory_data("summary"))
    print(f"Success: {result['success']}")
    if result["success"] and result["data"]:
        d = result["data"][0]
        print(f"  Total Products: {d.get('total_products', 0)}")
        print(f"  Stockouts: {d.get('stockout_count', 0)}")
        print(f"  Critical: {d.get('critical_count', 0)}")
        print(f"  Low: {d.get('low_count', 0)}")
        print(f"  Avg Days of Supply: {d.get('avg_days_of_supply', 0):.1f}")
    else:
        print(f"  Error: {result.get('error', 'No data')}")
    return result["success"]


def test_inventory_by_status():
    print("\n=== Testing Inventory by Status ===")
    result = json.loads(query_inventory_data("by_status"))
    print(f"Success: {result['success']}")
    if result["success"] and result["data"]:
        for s in result["data"]:
            print(f"  {s['status']}: {s['count']} items, avg {s['avg_days_of_supply']:.0f} days")
    else:
        print(f"  Error: {result.get('error', 'No data')}")
    return result["success"]


def test_low_stock():
    print("\n=== Testing Low Stock Items ===")
    result = json.loads(query_inventory_data("low_stock", top_n=5))
    print(f"Success: {result['success']}")
    if result["success"] and result["data"]:
        for item in result["data"][:5]:
            print(f"  {item['product_name']} ({item['region']}): {item['days_of_supply']:.0f} days")
    else:
        print(f"  Error: {result.get('error', 'No data')}")
    return result["success"]


def test_proactive_insights():
    print("\n=== Testing Proactive Insights ===")
    result = json.loads(get_proactive_insights(max_insights=3))
    print(f"Success: {result['success']}")
    if result["success"] and result.get("data"):
        for insight in result["data"][:3]:
            print(f"  [{insight.get('severity', '?')}] {insight.get('title', 'No title')}")
    elif result.get("narrative_summary"):
        print(f"  {result['narrative_summary'][:200]}")
    else:
        print(f"  No insights or error: {result.get('error', 'Unknown')}")
    return result["success"]


def test_daily_briefing():
    print("\n=== Testing Daily Briefing ===")
    result = json.loads(get_daily_briefing())
    print(f"Generated at: {result.get('generated_at', 'Unknown')}")
    if result.get("narrative"):
        print(f"Narrative:\n{result['narrative']}")
    if result.get("key_metrics"):
        print("Key metrics:")
        for m in result["key_metrics"]:
            print(f"  {m.get('metric', '?')}: {m.get('value', 0):,.0f}")
    return True


def main():
    print("=" * 60)
    print("🧪 Testing STIHL Analytics Agent Tools")
    print("=" * 60)

    tests = [
        ("Sales Summary", test_sales_summary),
        ("Top Products", test_top_products),
        ("Sales by Region", test_sales_by_region),
        ("Inventory Summary", test_inventory_summary),
        ("Inventory by Status", test_inventory_by_status),
        ("Low Stock", test_low_stock),
        ("Proactive Insights", test_proactive_insights),
        ("Daily Briefing", test_daily_briefing),
    ]

    results = []
    for name, test_fn in tests:
        try:
            success = test_fn()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    passed = sum(1 for _, s in results if s)
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name}")
    print(f"\nPassed: {passed}/{len(results)}")


if __name__ == "__main__":
    main()
