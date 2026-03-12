import opik
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from opik.integrations.langchain import OpikTracer

from settings import settings
from logging import logger

opik.configure()
opik_tracer = OpikTracer(tags=["langchain", "ollama", "mcp"])

# Using Ollama
model = ChatOllama(
    model="llama3.2:1b",
    temperature=0.7,
).with_config({"callbacks": [opik_tracer]})


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server_string_tools.py"],
    )
    # launch the server as a subprocess
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # initialize the communication between the client and the server
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)

            # Try out the tools via natural language
            msg1 = {"messages": "Reverse the string 'hello world'"}
            msg2 = {
                "messages": "How many words are in the sentence 'Model Context Protocol is powerful'?"
            }

            # TODO: apply query rewriting and save the optimised query

            res1 = await agent.ainvoke(msg1)
            # print("Reversed string result:", res1)
            for m in res1["messages"]:
                m.pretty_print()
            res2 = await agent.ainvoke(msg2)
            # print("Word count result:", res2)
            for m in res2["messages"]:
                m.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
