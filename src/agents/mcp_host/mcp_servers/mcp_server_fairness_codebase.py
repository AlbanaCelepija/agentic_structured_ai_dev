"""MCP server exposing pgvector-backed retrieval tools over indexed fairness toolkit codebases.

Tools
-----
search_fairlearn_code  — similarity search over the fairlearn codebase
search_holisticai_code — similarity search over the holisticai codebase
search_fairness_code   — cross-toolkit similarity search (fairlearn + holisticai)

Resources
---------
toolkit://{toolkit_name}  — metadata about a supported fairness toolkit

Prompts
-------
generate_fairness_code — prompt template for code generation using a fairness toolkit

Run (from the mcp_servers/ directory):
    python mcp_server_fairness_codebase.py
"""

import sys
from typing import Literal

import pandas as pd
from loguru import logger
from mcp.server.fastmcp import FastMCP

from indexing.config import settings
from indexing.indexer import get_embedding_model, get_vectorstore

# ---------------------------------------------------------------------------
# Server initialization
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "fairness_codebase",
    host="127.0.0.1",
    port=8082,
)

# ---------------------------------------------------------------------------
# Retriever bootstrap — shared embedding model + vectorstore connection.
# Initialized once at startup; tools reference module-level objects.
# ---------------------------------------------------------------------------

_embeddings = get_embedding_model()
_vectorstore = get_vectorstore(_embeddings)


def _retrieve(query: str, toolkit: str | None, k: int) -> list[str]:
    """Run similarity search and return formatted chunk strings.

    Each returned string contains the file path (from metadata) and
    the chunk content so the agent has full provenance.
    """
    search_kwargs: dict = {"k": k}
    if toolkit is not None:
        search_kwargs["filter"] = {"toolkit": toolkit}

    retriever = _vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs=search_kwargs,
    )
    docs = retriever.invoke(query)

    results = []
    for doc in docs:
        meta = doc.metadata
        header = (
            f"[toolkit={meta.get('toolkit', '?')} | "
            f"file={meta.get('file_path', '?')} | "
            f"type={meta.get('file_type', '?')}]"
        )
        results.append(f"{header}\n{doc.page_content}")

    return results


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search_fairlearn_code(query: str, k: int = 5) -> list[str]:
    """Search the indexed fairlearn source code and documentation.

    Use this tool to find concrete implementation examples, class/function
    signatures, and usage patterns from the fairlearn library when the user
    asks about fairness metrics, constraint-based mitigation, or anything
    fairlearn-specific.

    Args:
        query: Natural-language description of the code or concept to look up.
        k:     Number of code chunks to return (default 5).

    Returns:
        List of relevant code snippets with file provenance.
    """
    logger.info(f"[search_fairlearn_code] query={query!r} k={k}")
    return _retrieve(query, toolkit="fairlearn", k=k)


@mcp.tool()
def search_holisticai_code(query: str, k: int = 5) -> list[str]:
    """Search the indexed holisticai source code and documentation.

    Use this tool to find concrete implementation examples, class/function
    signatures, and usage patterns from the holisticai library when the user
    asks about fairness, explainability, robustness, or privacy operations
    supported by holisticai.

    Args:
        query: Natural-language description of the code or concept to look up.
        k:     Number of code chunks to return (default 5).

    Returns:
        List of relevant code snippets with file provenance.
    """
    logger.info(f"[search_holisticai_code] query={query!r} k={k}")
    return _retrieve(query, toolkit="holisticai", k=k)


@mcp.tool()
def search_fairness_code(query: str, k: int = 6) -> list[str]:
    """Search across ALL indexed fairness toolkits (fairlearn + holisticai).

    Use this tool when you are unsure which library to use, or when you need
    to compare implementations across toolkits for the same fairness concept
    (e.g. demographic parity, equalized odds, reweighing).

    Args:
        query: Natural-language description of the code or concept to look up.
        k:     Total number of code chunks to return across all toolkits (default 6).

    Returns:
        List of relevant code snippets with toolkit and file provenance.
    """
    logger.info(f"[search_fairness_code] query={query!r} k={k}")
    return _retrieve(query, toolkit=None, k=k)


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

@mcp.resource("toolkit://{toolkit_name}")
def get_toolkit_metadata(toolkit_name: str) -> dict:
    """Return catalog metadata for a fairness toolkit.

    Args:
        toolkit_name: One of the toolkit names in the catalog CSV.

    Returns:
        Dict with fields: tool, principle, documentation, codebase, domain,
        modality, provider.
    """
    catalog = pd.read_csv("tools_principles_catalog.csv")
    row = catalog[catalog["tool"] == toolkit_name]
    if row.empty:
        return {"error": f"Toolkit '{toolkit_name}' not found in catalog."}
    return row.iloc[0].dropna().to_dict()


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

@mcp.prompt()
def generate_fairness_code(
    toolkit: Literal["fairlearn", "holisticai"],
    task: str,
    fairness_concept: str,
) -> str:
    """Prompt template for generating fairness-aware ML code with a specific toolkit.

    Args:
        toolkit:          The fairness library to use ("fairlearn" or "holisticai").
        task:             ML task description, e.g. "binary classification on adult census data".
        fairness_concept: Fairness constraint or metric to apply,
                          e.g. "demographic parity", "equalized odds", "reweighing".

    Returns:
        A system+user prompt string ready to send to an LLM coding agent.
    """
    system = (
        "You are an expert ML engineer specialized in responsible AI. "
        "You write clean, idiomatic Python code using open-source fairness toolkits. "
        "Always use the retrieved code snippets from the vector store as your primary reference. "
        "Follow the toolkit's official API exactly as shown in the retrieved context."
    )
    user = (
        f"Generate Python code for the following task:\n\n"
        f"  Task            : {task}\n"
        f"  Toolkit         : {toolkit}\n"
        f"  Fairness concept: {fairness_concept}\n\n"
        f"Steps to follow:\n"
        f"1. Use the `search_{toolkit}_code` tool with a query about '{fairness_concept}' "
        f"to retrieve relevant implementation examples from the indexed codebase.\n"
        f"2. Write complete, runnable Python code based on the retrieved snippets.\n"
        f"3. Include inline comments explaining the fairness-specific parts.\n"
        f"4. Add a short section at the end interpreting the fairness metric results."
    )
    return f"SYSTEM:\n{system}\n\nUSER:\n{user}"


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting fairness codebase MCP server on port 8082 …")
    mcp.run(transport="streamable-http")
