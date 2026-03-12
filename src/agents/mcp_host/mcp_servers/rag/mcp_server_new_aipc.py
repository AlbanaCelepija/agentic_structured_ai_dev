import math
from mcp.server.fastmcp import FastMCP
from retrievers import load_faiss_retriever

mcp = FastMCP("AIPC")


retriever = load_faiss_retriever("evidently")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

          
@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b. Raises error if b is zero."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


@mcp.tool()
def square_root(x: float) -> float:
    """Return the square root of x."""
    if x < 0:
        raise ValueError("Cannot take square root of a negative number.")
    return math.sqrt(x)

@mcp.tool()
def factorial(n: int) -> int:
    """Return factorial of n."""
    print(n)
    if n < 0:
        print(n)
        raise ValueError("Factorial is not defined for negative numbers.")
    return math.factorial(n)

@mcp.tool()
def fairness_retriever(query: str):    
    """Return code snippet to detect data drift.
       Retrieve the most relevant documents from the evidently drift detection collection. 
       Use this tool when the user asks about data drift detection.

    Input:
        query: str -> The user query to retrieve the most relevant documents

    Output:
        context: str -> most relevant documents retrieved from a vector DB
    """
    docs = retriever.get_relevant_documents(query)
    print(docs)
    return [doc.page_content for doc in docs]


if __name__ == "__main__":
    #mcp.run(transport="stdio")
    mcp.run(transport="streamable-http")