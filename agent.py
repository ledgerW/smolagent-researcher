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

# configure the Phoenix tracer
tracer_provider = register(
  project_name=os.getenv("PHOENIX_PROJECT_NAME")
)

SmolagentsInstrumentor().instrument(tracer_provider=tracer_provider)




model = LiteLLMModel(
    "anthropic/claude-3-5-sonnet-latest",
    temperature=0.1,
    max_tokens=2000,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

web_agent = ToolCallingAgent(
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool()],
    model=model,
    max_steps=10,
    name="web_search",
    description="Runs web searches for you. Give it your query as an argument."
)

manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent]
)