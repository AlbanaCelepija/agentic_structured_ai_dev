from mcp.server.fastmcp import FactMCP
from utils import *

mcp = FactMCP("fairness_agent")

@mcp.tool()
def library_selection(operation_phase: str = "data_validation", requirement_aspect: str = "fairness"):
    return "This is the library selection tool"

@mcp.tool()
def codebase_indexing(code_repo: str):
    repo_name_evidently = code_repo.rstrip('/').split('/')[-1]
    extract_dir_evidently = f"./{repo_name_evidently}"
    download_repo = True
    if download_repo:
        download_and_extract_repo(code_repo, extract_dir_evidently)
    return "This is the codebase indexing tool"


@mcp.tool()
def code_generation(description: str):
    return "This is the code generation tool"


if __name__ == "__main__":
    print('Starting Fairness MCP server...', file=sys.stderr)
    mcp.run(transport="stdio")