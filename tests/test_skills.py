"""
Tests for the Skills Framework.
Run with: python -m tests.test_skills
"""
import unittest
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.skills import get_router, SkillRouter, SkillMatch


class TestSkillRouter(unittest.TestCase):
    def setUp(self):
        self.router = SkillRouter()

    def test_router_initialization(self):
        """Test that router initializes with all 7 default skills."""
        skills = self.router.list_skills()
        skill_names = {s["name"] for s in skills}
        expected = {"product_expert", "sales_analyst", "inventory_analyst", 
                   "insights_advisor", "dealer_analyst", "forecast_analyst", "trend_analyst"}
        self.assertEqual(skill_names, expected)
        print(f"[PASS] Router initialization - Found: {', '.join(sorted(skill_names))}")

    def test_product_skill_routing(self):
        """Test product queries route to product_expert."""
        queries = [
            "What chainsaw is best for professionals?",
            "Compare the MS 461 and MS 500i",
            "Tell me about the FS 91 trimmer",
            "Show me blower options",
            "What are the features of the MS 881?",
        ]
        for query in queries:
            match = self.router.route(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "product_expert", f"Query: {query}")
        print(f"[PASS] Product skill routing ({len(queries)} queries)")

    def test_sales_skill_routing(self):
        """Test sales queries route to sales_analyst."""
        queries = [
            "What was total revenue in 2024?",
            "Show me top products by sales",
            "Revenue by region",
            "YTD sales summary",
            "Q3 sales total",
        ]
        for query in queries:
            match = self.router.route(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "sales_analyst", f"Query: {query}")
        print(f"[PASS] Sales skill routing ({len(queries)} queries)")

    def test_inventory_skill_routing(self):
        """Test inventory queries route to inventory_analyst."""
        queries = [
            "What products are low on stock?",
            "Show me inventory levels",
            "Any stockouts?",
            "Days of supply report",
            "Critical stock items",
        ]
        for query in queries:
            match = self.router.route(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "inventory_analyst", f"Query: {query}")
        print(f"[PASS] Inventory skill routing ({len(queries)} queries)")

    def test_insights_skill_routing(self):
        """Test insights queries route to insights_advisor."""
        queries = [
            "Good morning!",
            "What should I know today?",
            "Any anomalies in March 2024?",
            "Give me a daily briefing",
            "What alerts do we have?",
        ]
        for query in queries:
            match = self.router.route(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "insights_advisor", f"Query: {query}")
        print(f"[PASS] Insights skill routing ({len(queries)} queries)")

    def test_trend_skill_routing(self):
        """Test trend queries route to trend_analyst."""
        queries = [
            "Show me YoY growth",
            "Month over month change",
            "What's the growth rate?",
            "Is momentum picking up?",
            "Compare this year vs last year",
        ]
        for query in queries:
            match = self.router.route(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "trend_analyst", f"Query: {query}")
        print(f"[PASS] Trend skill routing ({len(queries)} queries)")

    def test_forecast_skill_routing(self):
        """Test forecast queries route to forecast_analyst."""
        queries = [
            "What's the forecast for next quarter?",
            "Predict revenue for next month",
            "What are our seasonal patterns?",
            "Year-end projection",
            "When is peak season?",
        ]
        for query in queries:
            match = self.router.route(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "forecast_analyst", f"Query: {query}")
        print(f"[PASS] Forecast skill routing ({len(queries)} queries)")

    def test_dealer_skill_routing(self):
        """Test dealer queries route to dealer_analyst."""
        queries = [
            "Who are our top dealers?",
            "Show me dealer performance",
            "Dealer coverage gaps",
            "List our flagship dealers",
            "Dealer network summary",
        ]
        for query in queries:
            match = self.router.route(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "dealer_analyst", f"Query: {query}")
        print(f"[PASS] Dealer skill routing ({len(queries)} queries)")

    def test_confidence_scoring(self):
        """Test confidence scores work."""
        match = self.router.route("Compare MS 461 vs MS 500i chainsaw")
        self.assertIsNotNone(match)
        self.assertGreater(match.confidence, 0)
        print(f"[PASS] Confidence scoring - Score: {match.confidence:.2f}")

    def test_tool_availability(self):
        """Test each skill has appropriate tools."""
        expected = {
            "product_expert": ["search_products", "compare_products", "get_product_recommendations"],
            "sales_analyst": ["query_sales_data"],
            "inventory_analyst": ["query_inventory_data"],
            "insights_advisor": ["get_proactive_insights", "detect_anomalies_realtime", "get_daily_briefing"],
            "dealer_analyst": ["query_dealer_data"],
            "forecast_analyst": ["get_sales_forecast"],
            "trend_analyst": ["analyze_trends"],
        }
        for skill_name, tools in expected.items():
            skill = self.router.get_skill(skill_name)
            self.assertIsNotNone(skill)
            self.assertEqual(set(skill.tools), set(tools))
        print(f"[PASS] Tool availability ({len(expected)} skills)")

    def test_explain_routing(self):
        """Test explain_routing debug feature."""
        explanation = self.router.explain_routing("What chainsaw is best?")
        self.assertIn("product_expert", explanation)
        print(f"[PASS] Explain routing")

    def test_no_match_fallback(self):
        """Test behavior when no skill matches."""
        match = self.router.route("xyz123 random gibberish")
        self.assertIsNone(match)
        print(f"[PASS] No match / fallback handling")

    def test_priority_ordering(self):
        """Test skills are ordered by priority."""
        skills = self.router.skills
        priorities = [s.priority for s in skills]
        self.assertEqual(priorities, sorted(priorities, reverse=True))
        print(f"[PASS] Priority ordering")


def run_tests():
    print("=" * 60)
    print(" STIHL Analytics Agent - Skills Test Suite")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSkillRouter)
    stream = io.StringIO()
    runner = unittest.TextTestRunner(verbosity=0, stream=stream)
    result = runner.run(suite)

    print("=" * 60)
    print(" Test Summary")
    print("=" * 60)
    total = result.testsRun
    failures = len(result.failures) + len(result.errors)
    passed = total - failures
    print(f"Passed: {passed}/{total}")

    if failures > 0:
        print(f"WARNING: {failures} test(s) failed")
        for test, trace in result.failures + result.errors:
            clean = trace.encode('ascii', 'replace').decode('ascii')
            print(f"\n[FAIL] {test}:\n{clean}")
    else:
        print("All tests passed!")
    return failures == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
