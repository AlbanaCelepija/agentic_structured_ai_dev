from mcp import Tool, Server
from mcp.server.fastmcp import FastMCP
from rag_pipeline import RAGPipeline

rag = RAGPipeline()
mcp = FastMCP("rag-mcp-server")

@mcp.tool(
    name="rag_query",
    description="Run a Retrieval-Augmented Generation query. Input: {query: string}"
)
def rag_query(query: str):
    result = rag.run_rag(query)
    return {
        "answer": result["answer"],
        "retrieved_documents": result["docs"]
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
