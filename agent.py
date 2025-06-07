from dotenv import load_dotenv
load_dotenv()

import os
from phoenix.otel import register
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
import yaml
import pathlib

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


class CustomToolCallingAgent(ToolCallingAgent):
    def __init__(self, *args, **kwargs):
        # Load custom prompt templates from local YAML
        custom_prompt_templates = yaml.safe_load(
            pathlib.Path("modified_toolcalling_agent.yaml").read_text()
        )
        kwargs["prompt_templates"] = custom_prompt_templates
        super().__init__(*args, **kwargs)



# LLM
claude_llm = LiteLLMModel(
    "anthropic/claude-sonnet-4-20250514",
    temperature=0.1,
    max_tokens=2000,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


# Tool Calling Agents
web_search_agent = CustomToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    model=claude_llm,
    max_steps=5,
    name="web_search_agent",
    description="Runs web searches for you. Give it your query as an argument."
)

newsletter_agent = CustomToolCallingAgent(
    tools=[ai_policy_geopolitics_semantic_search],
    model=claude_llm,
    max_steps=5,
    name="ai_policy_geopolitics_search",
    description="Use this tool to search curated newsletters by thought-leaders in the fields of AI, Policy, Geopolitics, and Security."
)

arxiv_agent = CustomToolCallingAgent(
    tools=[arxiv_tool],
    model=claude_llm,
    max_steps=5,
    name="arxiv_search",
    description="Use this tool to search Arxiv for papers on AI, Policy, Geopolitics, and Security."
)

yahoo_finance_agent = CustomToolCallingAgent(
    tools=[yahoo_finance_search],
    model=claude_llm,
    max_steps=5,
    name="yahoo_finance_search",
    description="Use this tool to search for financial data for publicly traded companies. Input must be a ticker symbol. Example: 'AAPL'."
)


# Manager CodeAgent
manager_agent = CodeAgent(
    tools=[],
    model=claude_llm,
    managed_agents=[web_search_agent, newsletter_agent, arxiv_agent, yahoo_finance_agent],
    additional_authorized_imports=["time", "numpy", "pandas"],
    planning_interval=2
)