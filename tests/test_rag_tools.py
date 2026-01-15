"""
Tests for RAG tools - semantic product search, comparison, and recommendations.

Run with: python -m tests.test_rag_tools

These tests require:
- Databricks connection configured in .env
- Vector search endpoint 'stihl-vector-endpoint' running
- Vector index 'dbw_stihl_analytics.vectors.product_index' populated
"""
import json
import sys
from typing import Any


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"       {details}")


def test_search_products_basic():
    """Test basic semantic product search."""
    from agent.tools.rag_tools import search_products
    
    result = search_products("professional chainsaw for heavy logging")
    data = json.loads(result)
    
    passed = (
        data.get("status") == "success" and
        data.get("result_count", 0) > 0 and
        "products" in data
    )
    
    details = ""
    if passed:
        products = [p["product_name"] for p in data["products"][:3]]
        details = f"Found: {', '.join(products)}"
    else:
        details = f"Error: {data.get('message', 'Unknown error')}"
    
    print_result("Basic semantic search", passed, details)
    return passed


def test_search_products_with_category_filter():
    """Test search with category filter."""
    from agent.tools.rag_tools import search_products
    
    result = search_products("lightweight easy to use", category="Trimmers")
    data = json.loads(result)
    
    passed = data.get("status") == "success"
    if passed:
        # Verify all results are Trimmers
        for product in data.get("products", []):
            if product.get("category") != "Trimmers":
                passed = False
                break
    
    details = f"All results are Trimmers: {passed}" if data.get("status") == "success" else data.get("message", "")
    print_result("Category filter (Trimmers)", passed, details)
    return passed


def test_search_products_with_power_type_filter():
    """Test search with power type filter."""
    from agent.tools.rag_tools import search_products
    
    result = search_products("quiet operation for residential", power_type="Battery")
    data = json.loads(result)
    
    passed = data.get("status") == "success"
    if passed:
        for product in data.get("products", []):
            if product.get("power_type") != "Battery":
                passed = False
                break
    
    details = f"All results are Battery: {passed}" if data.get("status") == "success" else data.get("message", "")
    print_result("Power type filter (Battery)", passed, details)
    return passed


def test_search_products_with_weight_filter():
    """Test search with max weight post-filter."""
    from agent.tools.rag_tools import search_products
    
    result = search_products("chainsaw", max_weight=10.0)
    data = json.loads(result)
    
    passed = data.get("status") == "success"
    if passed:
        for product in data.get("products", []):
            weight = product.get("weight_lbs")
            if weight and weight > 10.0:
                passed = False
                break
    
    details = f"All results ≤ 10 lbs" if passed else "Found products over weight limit"
    print_result("Weight filter (max 10 lbs)", passed, details)
    return passed


def test_search_products_with_price_filter():
    """Test search with max price post-filter."""
    from agent.tools.rag_tools import search_products
    
    result = search_products("trimmer", max_price=300.0)
    data = json.loads(result)
    
    passed = data.get("status") == "success"
    if passed:
        for product in data.get("products", []):
            price = product.get("msrp")
            if price and price > 300.0:
                passed = False
                break
    
    details = f"All results ≤ $300" if passed else "Found products over price limit"
    print_result("Price filter (max $300)", passed, details)
    return passed


def test_search_products_combined_filters():
    """Test search with multiple filters combined."""
    from agent.tools.rag_tools import search_products
    
    result = search_products(
        query="powerful blower",
        category="Blowers",
        power_type="Gas",
        max_price=500.0
    )
    data = json.loads(result)
    
    passed = data.get("status") == "success"
    if passed:
        for product in data.get("products", []):
            if product.get("category") != "Blowers":
                passed = False
            if product.get("power_type") != "Gas":
                passed = False
            if product.get("msrp", 0) > 500.0:
                passed = False
    
    details = "All filters applied correctly" if passed else "Filter mismatch"
    print_result("Combined filters", passed, details)
    return passed


def test_compare_products_valid():
    """Test comparing two valid products."""
    from agent.tools.rag_tools import search_products, compare_products
    
    # First get valid product IDs
    search_result = search_products("chainsaw", top_k=2)
    search_data = json.loads(search_result)
    
    if search_data.get("status") != "success" or len(search_data.get("products", [])) < 2:
        print_result("Compare products", False, "Could not find products to compare")
        return False
    
    product_ids = [p["product_id"] for p in search_data["products"][:2]]
    
    result = compare_products(product_ids)
    data = json.loads(result)
    
    passed = (
        data.get("status") == "success" and
        data.get("products_compared") == 2 and
        len(data.get("comparison", [])) == 2
    )
    
    details = f"Compared: {product_ids}" if passed else data.get("message", "")
    print_result("Compare two products", passed, details)
    return passed


def test_compare_products_insufficient():
    """Test error handling with fewer than 2 products."""
    from agent.tools.rag_tools import compare_products
    
    result = compare_products(["MS-170"])
    data = json.loads(result)
    
    passed = (
        data.get("status") == "error" and
        "at least 2" in data.get("message", "")
    )
    
    details = "Correctly rejected single product" if passed else "Should have rejected"
    print_result("Compare insufficient products", passed, details)
    return passed


def test_get_product_recommendations():
    """Test product recommendations with use case."""
    from agent.tools.rag_tools import get_product_recommendations
    
    result = get_product_recommendations(
        use_case="weekend yard maintenance",
        budget=400.0,
        experience_level="homeowner"
    )
    data = json.loads(result)
    
    passed = data.get("status") == "success" and len(data.get("products", [])) > 0
    
    details = ""
    if passed:
        products = [p["product_name"] for p in data["products"][:3]]
        details = f"Recommended: {', '.join(products)}"
    
    print_result("Product recommendations", passed, details)
    return passed


def test_search_different_categories():
    """Test semantic search across different categories."""
    from agent.tools.rag_tools import search_products
    
    test_cases = [
        ("Chainsaws", "professional chainsaw"),
        ("Trimmers", "string trimmer for edges"),
        ("Blowers", "leaf blower"),
    ]
    
    all_passed = True
    for expected_category, query in test_cases:
        result = search_products(query, category=expected_category, top_k=2)
        data = json.loads(result)
        
        if data.get("status") != "success":
            all_passed = False
            continue
            
        for product in data.get("products", []):
            if product.get("category") != expected_category:
                all_passed = False
    
    print_result("Multi-category search", all_passed, f"Tested {len(test_cases)} categories")
    return all_passed


def run_all_tests():
    """Run all RAG tool tests."""
    print_header("STIHL Analytics Agent - RAG Tools Test Suite")
    
    tests = [
        test_search_products_basic,
        test_search_products_with_category_filter,
        test_search_products_with_power_type_filter,
        test_search_products_with_weight_filter,
        test_search_products_with_price_filter,
        test_search_products_combined_filters,
        test_compare_products_valid,
        test_compare_products_insufficient,
        test_get_product_recommendations,
        test_search_different_categories,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print_result(test.__name__, False, f"Exception: {e}")
            results.append(False)
    
    # Summary
    print_header("Test Summary")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All RAG tool tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
