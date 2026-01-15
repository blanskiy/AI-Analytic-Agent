"""
Tests for Skill Router and Skills.

Run with: python -m tests.test_skills

Tests verify:
- Skill pattern matching
- Routing accuracy
- Confidence scoring
- Tool availability
"""
import sys


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


def test_skill_router_initialization():
    """Test that router initializes with all skills."""
    from agent.skills import get_router
    
    router = get_router()
    skills = router.list_skills()
    
    expected_skills = {"product_expert", "sales_analyst", "inventory_analyst", "insights_advisor"}
    actual_skills = {s["name"] for s in skills}
    
    passed = expected_skills == actual_skills
    details = f"Found: {', '.join(actual_skills)}"
    
    print_result("Router initialization", passed, details)
    return passed


def test_product_skill_routing():
    """Test that product queries route to product_expert."""
    from agent.skills import route_query
    
    test_queries = [
        "What chainsaw is best for professional logging?",
        "Recommend a lightweight battery trimmer",
        "Compare the MS 500i and MS 462",
        "Products with anti-vibration feature",
        "Which blower should I buy for my yard?",
    ]
    
    all_passed = True
    for query in test_queries:
        match = route_query(query)
        if not match or match.skill_name != "product_expert":
            print_result(f"Product routing: '{query[:40]}...'", False, 
                        f"Got: {match.skill_name if match else 'None'}")
            all_passed = False
    
    if all_passed:
        print_result("Product skill routing (5 queries)", True, "All routed correctly")
    
    return all_passed


def test_sales_skill_routing():
    """Test that sales queries route to sales_analyst."""
    from agent.skills import route_query
    
    test_queries = [
        "What's our total revenue for 2024?",
        "Top selling products last quarter",
        "Sales trend month over month",
        "Revenue by region",
        "How much did we sell in Q3?",
    ]
    
    all_passed = True
    for query in test_queries:
        match = route_query(query)
        if not match or match.skill_name != "sales_analyst":
            print_result(f"Sales routing: '{query[:40]}...'", False,
                        f"Got: {match.skill_name if match else 'None'}")
            all_passed = False
    
    if all_passed:
        print_result("Sales skill routing (5 queries)", True, "All routed correctly")
    
    return all_passed


def test_inventory_skill_routing():
    """Test that inventory queries route to inventory_analyst."""
    from agent.skills import route_query
    
    test_queries = [
        "Current stock levels",
        "Products running low on inventory",
        "Any stockouts in Southwest?",
        "Days of supply by category",
        "Warehouse inventory status",
    ]
    
    all_passed = True
    for query in test_queries:
        match = route_query(query)
        if not match or match.skill_name != "inventory_analyst":
            print_result(f"Inventory routing: '{query[:40]}...'", False,
                        f"Got: {match.skill_name if match else 'None'}")
            all_passed = False
    
    if all_passed:
        print_result("Inventory skill routing (5 queries)", True, "All routed correctly")
    
    return all_passed


def test_insights_skill_routing():
    """Test that insight queries route to insights_advisor."""
    from agent.skills import route_query
    
    test_queries = [
        "Good morning!",
        "What should I know today?",
        "Any anomalies in March 2024?",
        "Critical issues?",
        "Give me a daily briefing",
    ]
    
    all_passed = True
    for query in test_queries:
        match = route_query(query)
        if not match or match.skill_name != "insights_advisor":
            print_result(f"Insights routing: '{query[:40]}...'", False,
                        f"Got: {match.skill_name if match else 'None'}")
            all_passed = False
    
    if all_passed:
        print_result("Insights skill routing (5 queries)", True, "All routed correctly")
    
    return all_passed


def test_confidence_scoring():
    """Test that more specific queries get higher confidence."""
    from agent.skills import route_query
    
    # Specific query should have higher confidence than vague one
    specific = route_query("Compare the MS 500i fuel-injected chainsaw versus MS 462 for professional logging")
    vague = route_query("chainsaw")
    
    passed = True
    if not specific or not vague:
        passed = False
        details = "One or both queries didn't match"
    elif specific.confidence <= vague.confidence:
        passed = False
        details = f"Specific ({specific.confidence:.2f}) should be > vague ({vague.confidence:.2f})"
    else:
        details = f"Specific: {specific.confidence:.2f}, Vague: {vague.confidence:.2f}"
    
    print_result("Confidence scoring", passed, details)
    return passed


def test_tools_availability():
    """Test that skills have correct tools assigned."""
    from agent.skills import get_router
    
    router = get_router()
    
    expected_tools = {
        "product_expert": {"search_products", "compare_products", "get_product_recommendations"},
        "sales_analyst": {"query_sales_data"},
        "inventory_analyst": {"query_inventory_data"},
        "insights_advisor": {"get_proactive_insights", "detect_anomalies_realtime", "get_daily_briefing"},
    }
    
    all_passed = True
    for skill_name, expected in expected_tools.items():
        skill = router.get_skill(skill_name)
        actual = set(skill.tools)
        if actual != expected:
            print_result(f"Tools for {skill_name}", False, f"Expected {expected}, got {actual}")
            all_passed = False
    
    if all_passed:
        print_result("Tool availability (4 skills)", True, "All tools correctly assigned")
    
    return all_passed


def test_explain_routing():
    """Test the explain_routing debug function."""
    from agent.skills import get_router
    
    router = get_router()
    explanation = router.explain_routing("What chainsaw is best for professionals?")
    
    passed = (
        "product_expert" in explanation and
        "confidence" in explanation.lower() and
        "✅ Selected" in explanation
    )
    
    details = "Explanation includes skill, confidence, and selection" if passed else "Missing expected content"
    print_result("Explain routing", passed, details)
    return passed


def test_no_match_fallback():
    """Test behavior when no skill matches."""
    from agent.skills import get_router
    
    router = get_router()
    
    # Very generic query that shouldn't strongly match any skill
    match = router.route("hello there how are you doing today")
    
    # Either no match (None) or low confidence match
    if match is None:
        passed = True
        details = "Correctly returned None for ambiguous query"
    elif match.confidence < 0.5:
        passed = True
        details = f"Low confidence match: {match.skill_name} ({match.confidence:.2f})"
    else:
        # Insights might match due to greeting pattern - that's actually correct
        if match.skill_name == "insights_advisor":
            passed = True
            details = f"Matched greeting pattern: {match.skill_name}"
        else:
            passed = False
            details = f"Unexpected high confidence: {match.skill_name} ({match.confidence:.2f})"
    
    print_result("No match / fallback handling", passed, details)
    return passed


def test_priority_ordering():
    """Test that skills are checked in priority order."""
    from agent.skills import get_router
    
    router = get_router()
    skills = router.skills  # Should be sorted by priority
    
    priorities = [s.priority for s in skills]
    passed = priorities == sorted(priorities, reverse=True)
    
    skill_order = [(s.name, s.priority) for s in skills]
    details = f"Order: {skill_order}"
    
    print_result("Priority ordering", passed, details)
    return passed


def run_all_tests():
    """Run all skill tests."""
    print_header("STIHL Analytics Agent - Skills Test Suite")
    
    tests = [
        test_skill_router_initialization,
        test_product_skill_routing,
        test_sales_skill_routing,
        test_inventory_skill_routing,
        test_insights_skill_routing,
        test_confidence_scoring,
        test_tools_availability,
        test_explain_routing,
        test_no_match_fallback,
        test_priority_ordering,
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
        print("\n🎉 All skill tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
