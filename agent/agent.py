"""
STIHL Analytics Agent - Main Agent Orchestrator

This module defines the AI agent using Azure AI Foundry SDK,
registering all tools and configuring the system prompt.
"""

import json
from typing import Any, Callable
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentThread,
    MessageRole,
    ToolSet,
    FunctionTool,
)
from azure.identity import DefaultAzureCredential

from config.settings import get_config
from agent.prompts.system_prompt import SYSTEM_PROMPT
from agent.tools import TOOL_FUNCTIONS, TOOL_DEFINITIONS


class STIHLAnalyticsAgent:
    """
    STIHL Analytics Agent using Azure AI Foundry SDK.

    This agent:
    1. Connects to Azure AI Foundry project
    2. Uses GPT-4o-mini for reasoning
    3. Executes tools against Databricks data
    4. Provides proactive insights
    """

    def __init__(self):
        self.config = get_config()
        self.client = self._create_client()
        self.agent = None
        self.tools = self._create_tools()

    def _create_client(self) -> AIProjectClient:
        """Create Azure AI Foundry project client."""
        credential = DefaultAzureCredential()
        connection_string = self.config.ai_foundry.get_connection_string()

        return AIProjectClient.from_connection_string(
            conn_str=connection_string,
            credential=credential,
        )

    def _create_tools(self) -> ToolSet:
        """Create toolset with all agent capabilities."""
        tools = ToolSet()

        for tool_def in TOOL_DEFINITIONS:
            tools.add(FunctionTool(
                name=tool_def["function"]["name"],
                description=tool_def["function"]["description"],
                parameters=tool_def["function"]["parameters"],
            ))

        return tools

    def create_agent(self) -> str:
        """Create the agent in Azure AI Foundry."""
        self.agent = self.client.agents.create_agent(
            model=self.config.openai.deployment,
            name="STIHL-Analytics-Agent",
            instructions=SYSTEM_PROMPT,
            tools=self.tools,
        )
        return self.agent.id

    def create_thread(self) -> AgentThread:
        """Create a new conversation thread."""
        return self.client.agents.create_thread()

    def chat(self, thread_id: str, user_message: str) -> str:
        """
        Send a message and get a response.

        Args:
            thread_id: Conversation thread ID
            user_message: User's message

        Returns:
            Agent's response text
        """
        if not self.agent:
            raise ValueError("Agent not created. Call create_agent() first.")

        self.client.agents.create_message(
            thread_id=thread_id,
            role=MessageRole.USER,
            content=user_message,
        )

        run = self.client.agents.create_run(
            thread_id=thread_id,
            agent_id=self.agent.id,
        )

        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                run = self._handle_tool_calls(thread_id, run)
            else:
                import time
                time.sleep(0.5)
                run = self.client.agents.get_run(
                    thread_id=thread_id,
                    run_id=run.id,
                )

        messages = self.client.agents.list_messages(thread_id=thread_id)

        for msg in messages.data:
            if msg.role == MessageRole.ASSISTANT:
                return msg.content[0].text.value

        return "No response generated."

    def _handle_tool_calls(self, thread_id: str, run) -> Any:
        """Execute tool calls and submit results."""
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if function_name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[function_name](**arguments)
            else:
                result = json.dumps({"error": f"Unknown function: {function_name}"})

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": result,
            })

        return self.client.agents.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs,
        )

    def cleanup(self):
        """Delete the agent when done."""
        if self.agent:
            self.client.agents.delete_agent(self.agent.id)


def create_agent() -> STIHLAnalyticsAgent:
    """Factory function to create and initialize the agent."""
    agent = STIHLAnalyticsAgent()
    agent.create_agent()
    return agent


if __name__ == "__main__":
    # Quick test
    print("Creating STIHL Analytics Agent...")
    agent = create_agent()
    thread = agent.create_thread()

    print("\nTesting proactive greeting...")
    response = agent.chat(thread.id, "Good morning! What should I know today?")
    print(response)

    print("\nTesting sales query...")
    response = agent.chat(thread.id, "What were our top selling products last quarter?")
    print(response)

    agent.cleanup()
    print("\nAgent cleaned up.")
