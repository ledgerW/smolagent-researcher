import os
import asyncio

from smolagents import tool, Tool
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.agents import load_tools
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

from gdelt_v2 import query_doc, query_gkg
from gdelt_v3 import get_entities, get_events

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
namespace = os.getenv("PINECONE_NAMESPACE")


@tool
def ai_policy_geopolitics_semantic_search(
    query: str,
    k: int = 3,
) -> str:
    """
    Use this tool to search curated newsletters by thought-leaders in the fields of AI, Policy, Geopolitics, and Security.
    This is a tool that returns a list of langchain documents that are semantically similar to the query.

    Args:
        query: The query to search for.
        k: The number of documents to return.
    """
    response = index.query(
        namespace=namespace,
        vector=embeddings.embed_query(query),
        top_k=k,
        include_metadata=True,
    )
    formatted_results = []
    for match in response["matches"]:
        metadata = match["metadata"]
        formatted_results.append(
            f"Title: {metadata['title']}\n"
            f"Author: {metadata['author']}\n"
            f"Date: {metadata['date']}\n"
            f"Source: {metadata['source']}\n"
            f"URL: {metadata['article_url']}\n"
            f"Content:\n{metadata['content']}"
        )
    return "\n\n".join(formatted_results)


@tool
def yahoo_finance_search(company_ticker: str) -> str:
    """
    Use this tool to search for financial data for publicly traded companies.
    Input must be a ticker symbol.

    Args:
        company_ticker: The ticker of the company to search for. Example: "AAPL".
    """
    tool = YahooFinanceNewsTool()
    return tool.invoke(company_ticker)


# Arxiv Tool
arxiv_tool = Tool.from_langchain(load_tools(["arxiv"])[0])


@tool
def query_gdelt_v2_doc(
    query: str,
    mode: str = "TimelineTone",
    start: str | None = None,
    end: str | None = None,
) -> dict:
    """
    Use this tool to query the GDELT V2 Full-Text API for articles related to the search query.

    Args:
        query: The search query to run.
        mode: Timeline mode for the API. Defaults to "TimelineTone".
        start: Optional start datetime in YYYYMMDDhhmmss format.
        end: Optional end datetime in YYYYMMDDhhmmss format.
    """
    return asyncio.run(query_doc(query=query, mode=mode, start=start, end=end)).__dict__


@tool
def query_gdelt_v2_gkg(query: str, themes: list[str] | None = None) -> dict:
    """
    Use this tool to query the GDELT V2 GKG API. It returns Global Knowledge Graph records matching the query.

    Args:
        query: The search query to run.
        themes: Optional list of themes to filter results.
    """
    return asyncio.run(query_gkg(query=query, themes=themes)).__dict__


@tool
def query_gdelt_v3_entities(start: str, end: str, query: str) -> dict:
    """
    Use this tool to query the experimental GDELT V3 entities API. It returns entities found in the specified time range.

    Args:
        start: Start datetime in YYYYMMDDhhmmss format.
        end: End datetime in YYYYMMDDhhmmss format.
        query: The search query to run.
    """
    return asyncio.run(get_entities(start=start, end=end, query=query)).__dict__


@tool
def query_gdelt_v3_events(start: str, end: str, query: str) -> dict:
    """
    Use this tool to query the experimental GDELT V3 events API. It returns events in the specified time range.

    Args:
        start: Start datetime in YYYYMMDDhhmmss format.
        end: End datetime in YYYYMMDDhhmmss format.
        query: The search query to run.
    """
    return asyncio.run(get_events(start=start, end=end, query=query)).__dict__

