import os

from smolagents import tool, Tool
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
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
    #vector_store = PineconeVectorStore(index=index, namespace=namespace, embedding=embeddings)
    #retriever = vector_store.as_retriever(search_kwargs={"k": k})
    #docs = retriever.invoke(query)
    #formatted_docs = []
    #for i, doc in enumerate(docs, 1):
    #    formatted_docs.append(
    #        f"\nDocument {i}:"
    #        f"\nContent:\n{doc.page_content}"
    #        f"\nMetadata:\n{doc.metadata}\n"
    #    )
    #return "\n\n".join(formatted_docs)
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
def yahoo_finance_search(query: str) -> str:
    """
    Use this tool to search for financial news and information from Yahoo Finance.
    This tool returns relevant news articles and financial information based on your query.
    
    Args:
        query: The search query for finding financial news and information.
    """
    tool = YahooFinanceNewsTool()
    return tool.invoke(query)


# Arxive Tool
arxiv_tool = Tool.from_langchain(load_tools(["arxiv"])[0])

# Yahoo Finance Tool
#google_finance_tool = Tool.from_langchain(load_tools(["google-finance"])[0])