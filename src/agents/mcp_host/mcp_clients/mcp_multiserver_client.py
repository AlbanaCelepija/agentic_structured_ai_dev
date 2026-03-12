from langchain_mcp_adapters.client import MultiServerMCPClient  
from langchain.agents import create_agent


client = MultiServerMCPClient(  
    {
        "tai_engineers": {
            "transport": "stdio",  # Local subprocess communication
            "command": "python",
            "args": ["../mcp_servers/mcp_server_tai_engineers.py"],
        }
    }
)

tools = await client.get_tools()  
agent = create_agent(
    "claude-sonnet-4-5-20250929",
    tools  
)
math_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
)
weather_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
)