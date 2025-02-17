from dotenv import load_dotenv
load_dotenv()

import os
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor

from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    DuckDuckGoSearchTool,
    VisitWebpageTool,
    LiteLLMModel,
)

from tools import ai_policy_geopolitics_semantic_search, arxiv_tool, yahoo_finance_search

# configure the Phoenix tracer
tracer_provider = register(
  project_name=os.getenv("PHOENIX_PROJECT_NAME")
)

SmolagentsInstrumentor().instrument(tracer_provider=tracer_provider)

# LLM
claude_llm = LiteLLMModel(
    "anthropic/claude-3-5-sonnet-latest",
    temperature=0.1,
    max_tokens=2000,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Tool Calling Agents
web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    model=claude_llm,
    max_steps=10,
    name="web_search",
    description="Runs web searches for you. Give it your query as an argument."
)

newsletter_agent = ToolCallingAgent(
    tools=[ai_policy_geopolitics_semantic_search],
    model=claude_llm,
    max_steps=5,
    name="ai_policy_geopolitics_search",
    description="Use this tool to search curated newsletters by thought-leaders in the fields of AI, Policy, Geopolitics, and Security."
)

arxiv_agent = ToolCallingAgent(
    tools=[arxiv_tool],
    model=claude_llm,
    max_steps=5,
    name="arxiv_search",
    description="Use this tool to search Arxiv for papers on AI, Policy, Geopolitics, and Security."
)

yahoo_finance_agent = ToolCallingAgent(
    tools=[yahoo_finance_search],
    model=claude_llm,
    max_steps=5,
    name="yeahoo_finance_search",
    description="Use this tool to search for financial data for publicly traded companies. Input must be a ticker symbol. Example: 'AAPL'."
)

manager_agent = CodeAgent(
    tools=[],
    model=claude_llm,
    managed_agents=[web_agent, newsletter_agent, arxiv_agent, yahoo_finance_agent],
    additional_authorized_imports=["time", "numpy", "pandas"]
)