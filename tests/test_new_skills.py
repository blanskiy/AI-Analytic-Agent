"""
Tests for new skills: DealerSkill, ForecastSkill, TrendSkill.

Run with: python -m tests.test_new_skills
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.skills import get_router, SkillRouter
from agent.skills.dealer_skill import DealerSkill
from agent.skills.forecast_skill import ForecastSkill
from agent.skills.trend_skill import TrendSkill


class TestDealerSkill(unittest.TestCase):
    """Test DealerSkill routing and configuration."""
    
    def setUp(self):
        self.skill = DealerSkill()
        self.router = SkillRouter()
    
    def test_skill_properties(self):
        """Test skill has required properties."""
        self.assertEqual(self.skill.name, "dealer_analyst")
        self.assertIn("query_dealer_data", self.skill.tools)
        self.assertEqual(self.skill.priority, 22)  # Updated priority
    
    def test_dealer_performance_routing(self):
        """Test routing for dealer performance queries."""
        queries = [
            "Who are our top dealers?",
            "Show me dealer performance",
            "Which dealers are underperforming?",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "dealer_analyst")
    
    def test_territory_routing(self):
        """Test routing for territory/coverage queries."""
        queries = [
            "Where do we have coverage gaps?",
            "Which territories need more dealers?",
            "Dealer network summary",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")
    
    def test_dealer_type_routing(self):
        """Test routing for dealer type queries."""
        queries = [
            "List our flagship dealers",
            "Authorized dealer count",
            "Show me dealer breakdown by type",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")


class TestForecastSkill(unittest.TestCase):
    """Test ForecastSkill routing and configuration."""
    
    def setUp(self):
        self.skill = ForecastSkill()
        self.router = SkillRouter()
    
    def test_skill_properties(self):
        """Test skill has required properties."""
        self.assertEqual(self.skill.name, "forecast_analyst")
        self.assertIn("get_sales_forecast", self.skill.tools)
        self.assertEqual(self.skill.priority, 24)  # Updated priority
    
    def test_forecast_routing(self):
        """Test routing for forecast queries."""
        queries = [
            "What's the forecast for next quarter?",
            "Predict revenue for next month",
            "Project sales through year end",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "forecast_analyst")
    
    def test_seasonal_routing(self):
        """Test routing for seasonal pattern queries."""
        queries = [
            "What are our seasonal patterns?",
            "When is our peak season?",
            "Which months are busiest?",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")
    
    def test_projection_routing(self):
        """Test routing for projection queries."""
        queries = [
            "What's our year-end projection?",
            "Are we on track to hit our target?",
            "What will annual revenue be?",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")


class TestTrendSkill(unittest.TestCase):
    """Test TrendSkill routing and configuration."""
    
    def setUp(self):
        self.skill = TrendSkill()
        self.router = SkillRouter()
    
    def test_skill_properties(self):
        """Test skill has required properties."""
        self.assertEqual(self.skill.name, "trend_analyst")
        self.assertIn("analyze_trends", self.skill.tools)
        self.assertEqual(self.skill.priority, 19)  # Updated priority
    
    def test_yoy_routing(self):
        """Test routing for year-over-year queries."""
        queries = [
            "Compare this year vs last year",
            "Show me YoY growth",
            "Revenue versus last year",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")
            self.assertEqual(match.skill_name, "trend_analyst")
    
    def test_mom_routing(self):
        """Test routing for month-over-month queries."""
        queries = [
            "How did we do compared to last month?",
            "Month over month change",
            "MoM growth rate",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")
    
    def test_growth_routing(self):
        """Test routing for growth queries."""
        queries = [
            "What's our growth rate?",
            "Show me revenue growth trends",
            "Is the business growing?",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")
    
    def test_momentum_routing(self):
        """Test routing for momentum queries."""
        queries = [
            "Is momentum picking up?",
            "Are sales accelerating?",
            "What's the trend direction?",
        ]
        for query in queries:
            match = self.skill.matches(query)
            self.assertIsNotNone(match, f"Should match: {query}")


class TestRouterWithNewSkills(unittest.TestCase):
    """Test router correctly registers and routes to new skills."""
    
    def setUp(self):
        self.router = SkillRouter()
    
    def test_all_skills_registered(self):
        """Test all 7 skills are registered."""
        skills = self.router.list_skills()
        skill_names = [s["name"] for s in skills]
        
        expected = [
            "insights_advisor",
            "product_expert",
            "sales_analyst",
            "inventory_analyst",
            "dealer_analyst",
            "forecast_analyst",
            "trend_analyst",
        ]
        
        for name in expected:
            self.assertIn(name, skill_names, f"Skill {name} should be registered")
    
    def test_skill_priority_order(self):
        """Test skills are sorted by priority."""
        skills = self.router.list_skills()
        priorities = [s["priority"] for s in skills]
        
        # Should be descending (highest priority first)
        self.assertEqual(priorities, sorted(priorities, reverse=True))
    
    def test_dealer_query_routing(self):
        """Test dealer queries route correctly."""
        match = self.router.route("Who are our top dealers?")
        self.assertIsNotNone(match)
        self.assertEqual(match.skill_name, "dealer_analyst")
    
    def test_forecast_query_routing(self):
        """Test forecast queries route correctly."""
        match = self.router.route("What's the sales forecast?")
        self.assertIsNotNone(match)
        self.assertEqual(match.skill_name, "forecast_analyst")
    
    def test_trend_query_routing(self):
        """Test trend queries route correctly."""
        match = self.router.route("Show me YoY growth")
        self.assertIsNotNone(match)
        self.assertEqual(match.skill_name, "trend_analyst")
    
    def test_skill_disambiguation(self):
        """Test router picks correct skill for ambiguous queries."""
        # "What will next quarter look like?" -> forecast (future focus)
        match = self.router.route("What will next quarter look like?")
        self.assertIsNotNone(match)
        self.assertEqual(match.skill_name, "forecast_analyst")


class TestToolDefinitions(unittest.TestCase):
    """Test new tool definitions are properly registered."""
    
    def test_tool_functions_available(self):
        """Test new tool functions are in TOOL_FUNCTIONS."""
        from agent.tools import TOOL_FUNCTIONS
        
        expected_tools = [
            "query_dealer_data",
            "get_sales_forecast",
            "analyze_trends",
        ]
        
        for tool in expected_tools:
            self.assertIn(tool, TOOL_FUNCTIONS, f"Tool {tool} should be registered")
    
    def test_tool_definitions_available(self):
        """Test new tool definitions are in TOOL_DEFINITIONS."""
        from agent.tools import TOOL_DEFINITIONS
        
        tool_names = [t["function"]["name"] for t in TOOL_DEFINITIONS]
        
        expected_tools = [
            "query_dealer_data",
            "get_sales_forecast",
            "analyze_trends",
        ]
        
        for tool in expected_tools:
            self.assertIn(tool, tool_names, f"Tool definition {tool} should be registered")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing New Skills: Dealer, Forecast, Trend")
    print("=" * 60)
    
    # Run tests
    unittest.main(verbosity=2)
