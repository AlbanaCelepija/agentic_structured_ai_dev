"""Build a pgvector-backed retriever for use inside the MCP tool.

Typical usage inside the MCP server:

    from indexing.retriever import get_fairness_retriever, get_fairness_retriever_tool

    retriever = get_fairness_retriever(toolkit="fairlearn", k=5)
    tool      = get_fairness_retriever_tool(toolkit="fairlearn")
"""

from langchain.tools.retriever import create_retriever_tool
from langchain_core.vectorstores import VectorStoreRetriever

from .indexer import get_embedding_model, get_vectorstore


def get_fairness_retriever(
    toolkit: str | None = None,
    k: int = 5,
) -> VectorStoreRetriever:
    """Return a similarity retriever for *toolkit* (or all toolkits if None).

    Args:
        toolkit: "fairlearn", "holisticai", or None for cross-toolkit search.
        k: Number of chunks to retrieve.
    """
    embeddings = get_embedding_model()
    vectorstore = get_vectorstore(embeddings)

    search_kwargs: dict = {"k": k}
    if toolkit is not None:
        # pgvector metadata filter – langchain_postgres uses JSONB operators
        search_kwargs["filter"] = {"toolkit": toolkit}

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )


def get_fairness_retriever_tool(
    toolkit: str | None = None,
    k: int = 5,
):
    """Wrap the retriever as a LangChain tool for use in an agent or MCP server."""
    retriever = get_fairness_retriever(toolkit=toolkit, k=k)

    if toolkit:
        name = f"retrieve_{toolkit}_code"
        description = (
            f"Search the {toolkit} source code and documentation. "
            f"Use this tool to find implementation examples, API usage, "
            f"and patterns for fairness-aware machine learning with {toolkit}."
        )
    else:
        name = "retrieve_fairness_toolkit_code"
        description = (
            "Search across fairlearn and holisticai source code and documentation. "
            "Use this tool to find implementation examples, API usage, and patterns "
            "for fairness-aware machine learning."
        )

    return create_retriever_tool(retriever, name, description)
