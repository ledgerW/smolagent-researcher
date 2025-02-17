import os

from smolagents import tool, Tool
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.agents import load_tools
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool


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
        include_metadata=True
    )
    formatted_results = []
    for match in response['matches']:
        metadata = match['metadata']
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


# Arxive Tool
arxiv_tool = Tool.from_langchain(load_tools(["arxiv"])[0])