"""
STIHL Analytics Agent - Real Function Calling Orchestrator

Uses Azure OpenAI chat completions with tools to execute live queries
against Databricks SQL warehouse.
"""

import json
import os
from typing import Optional
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our tool functions
from agent.tools.sales_tools import query_sales_data, SALES_TOOL_DEFINITION
from agent.tools.inventory_tools import query_inventory_data, INVENTORY_TOOL_DEFINITION
from agent.tools.insights_tools import (
    get_proactive_insights,
    detect_anomalies_realtime,
    get_daily_briefing,
    PROACTIVE_INSIGHTS_TOOL_DEFINITION,
    DETECT_ANOMALIES_TOOL_DEFINITION,
    DAILY_BRIEFING_TOOL_DEFINITION,
)

# System prompt for the agent
SYSTEM_PROMPT = """You are STIHL's Sales & Inventory Analytics Agent - an AI assistant that helps 
analysts understand sales performance, inventory status, and business trends.

## Your Key Capabilities
1. **Proactive Insights**: Surface anomalies and alerts WITHOUT being asked
2. **Natural Language Queries**: Convert questions into data analysis
3. **Actionable Recommendations**: Don't just show data, suggest what to do

## Conversation Behavior
- When a user starts with greetings like "Hi", "Good morning", or "What should I know?":
  → IMMEDIATELY call get_daily_briefing or get_proactive_insights
  → Lead with the most critical insight, not a generic greeting

- For sales questions → call query_sales_data with appropriate query_type
- For inventory questions → call query_inventory_data with appropriate query_type
- For anomaly detection → call detect_anomalies_realtime

## Response Style
- Lead with the key insight or answer
- Be specific with numbers and percentages
- End with a recommended action or follow-up question
- Be conversational but professional

## Available Tools
1. query_sales_data - Get sales metrics, trends, top products, regional performance
2. query_inventory_data - Get stock levels, stockouts, days of supply
3. get_proactive_insights - Get pre-computed anomalies and alerts (call at conversation start!)
4. detect_anomalies_realtime - Run real-time anomaly detection on metrics
5. get_daily_briefing - Get comprehensive daily overview with metrics and insights
"""

# Map function names to actual functions
TOOL_FUNCTIONS = {
    "query_sales_data": query_sales_data,
    "query_inventory_data": query_inventory_data,
    "get_proactive_insights": get_proactive_insights,
    "detect_anomalies_realtime": detect_anomalies_realtime,
    "get_daily_briefing": get_daily_briefing,
}

# All tool definitions for the API
TOOLS = [
    SALES_TOOL_DEFINITION,
    INVENTORY_TOOL_DEFINITION,
    PROACTIVE_INSIGHTS_TOOL_DEFINITION,
    DETECT_ANOMALIES_TOOL_DEFINITION,
    DAILY_BRIEFING_TOOL_DEFINITION,
]


class STIHLAnalyticsAgent:
    """
    Real AI agent using Azure OpenAI function calling with Databricks tools.
    """

    def __init__(self):
        """Initialize the Azure OpenAI client."""
        self.client = AzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2024-08-01-preview",
        )
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT", "gpt-4o-mini")
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def chat(self, user_message: str, max_tool_calls: int = 5) -> str:
        """
        Send a message and get a response, handling function calls automatically.

        Args:
            user_message: The user's message
            max_tool_calls: Maximum number of tool call iterations (prevent infinite loops)

        Returns:
            The agent's final response
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        tool_call_count = 0

        while tool_call_count < max_tool_calls:
            # Call Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=self.conversation_history,
                tools=TOOLS,
                tool_choice="auto",
            )

            response_message = response.choices[0].message

            # Check if we're done (no more tool calls)
            if not response_message.tool_calls:
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_message.content
                })
                return response_message.content

            # Process tool calls
            self.conversation_history.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in response_message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"  🔧 Calling {function_name}({function_args})")

                # Execute the function
                if function_name in TOOL_FUNCTIONS:
                    try:
                        result = TOOL_FUNCTIONS[function_name](**function_args)
                    except Exception as e:
                        result = json.dumps({"error": str(e)})
                else:
                    result = json.dumps({"error": f"Unknown function: {function_name}"})

                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

            tool_call_count += 1

        return "I've reached the maximum number of tool calls. Please try a more specific question."

    def reset_conversation(self):
        """Clear conversation history and start fresh."""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]


def main():
    """Interactive chat loop for testing."""
    print("=" * 60)
    print("🤖 STIHL Analytics Agent - Live Function Calling")
    print("=" * 60)
    print("Type 'quit' to exit, 'reset' to clear conversation\n")

    agent = STIHLAnalyticsAgent()

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("Goodbye!")
                break
            if user_input.lower() == "reset":
                agent.reset_conversation()
                print("Conversation reset.")
                continue

            print("\n🤖 Agent: ", end="")
            response = agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
