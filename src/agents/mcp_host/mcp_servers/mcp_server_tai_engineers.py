import json
import os
from typing import List

from rag.retrievers import load_faiss_retriever
import pandas as pd
from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server
mcp = FastMCP("research", host="127.0.0.1",
              port=8081)


@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverses the given string."""
    return text[::-1]


@mcp.tool()
def count_words(text: str) -> int:
    """Counts the number of words in a sentence."""
    return len(text.split())

@mcp.tool()
def fairness_retrieval_tool(engineer: str):  
    """
    Docstring for fairness_retriever
    
    Args:
        engineer: The kind of engineer we are interested in requirement dimension implementation

    Returns:
        A set of documents related to the engineer that will enrich the context for the LLM
    """  
    return load_faiss_retriever(engineer)


@mcp.tool()
def index_codebase(library_name: str, library_codebase_url: str):
    """ using the embedding model to index the codebase and store it in a vector database"""
    return True

# Resources in MCP are read-only data exposed by the server that the LLM-based application can access without needing to use a tool.
@mcp.resource("opentoolkits://{principle}/{operation_category}")
def get_opentoolkit(principle: str, operation_category: str):
    """
    Get a list of open source libraries or toolkits that can be used to implement code for a given principle and operation category.

    Args:
        name: The name of the opentoolkit to retrieve.

    Returns:
        The opentoolkit with the given name.
    """
    toolkits_df = pd.read_csv("tools_principles_catalog.csv")
    toolkits = toolkits_df[(toolkits_df["principle"] == principle) and 
                           (toolkits_df["operation_category"] == operation_category)]
    return toolkits


# Add a prompt
# Prompt templates remove the burden of prompt engineering from users by providing predefined, parameterized prompts that can be reused.
@mcp.prompt()
def greet_user(operation_name: str) -> str:
    """Generate a prompt for implementing one operation category"""
    system_prompt = """You are a knowledgeable coding assistant whose goal it is to help us solve coding tasks. 
                        Use the instructions below and the tools available to you to assist the user.
                        Answer the user's query based only on the information provided in the context."""
    operations = {
        "data_profiling": """Includes procedures code that generate reports with specific characteristics of data or analyze data distribution.""",
        "data_validation": """Includes code procedures that calidate the quality of training or production data to identify issues that could impact model performance.""",
        "data_preprocessing": """Includes code procedures that apply data cleaning, data augmentation, type conversion, evaluate bias or discrimination issues on data.""",
        "data_documentation": """Includes code procedures that produces human readable documentation in order to facilitate knowledge transfer and increase transparency about data characteristics that are obtained during data profiling operation categories.""",
    }

    return f"{system_prompt}  {operations.get(operation_name, operations['data_profiling'])} "


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
