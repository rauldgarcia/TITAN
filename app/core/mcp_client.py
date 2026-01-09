import shutil
import logging
from langchain_core.tools import Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


async def load_mcp_tools():
    """
    Connects to the local MCP Finance Server and converts its capabilities
    into LangChain Tools usable by our Agent.
    """
    python_executable = shutil.which("python")
    server_params = StdioServerParameters(
        command=python_executable,
        args=["app/mcp/finance_server.py"],
    )

    tools = []

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                mcp_tools = await session.list_tools()

                for tool in mcp_tools.tools:

                    async def _tool_wrapper(query: str, tool_name=tool.name):
                        async with stdio_client(server_params) as (r, w):
                            async with ClientSession(r, w) as s:
                                await s.initialize()
                                result = await s.call_tool(
                                    tool_name, arguments={"ticker": query}
                                )
                                return result.content[0].text

                    lc_tool = Tool(
                        name=tool.name,
                        func=None,
                        coroutine=_tool_wrapper,
                        description=tool.description,
                    )
                    tools.append(lc_tool)
                    logger.info(f"MCP Tool Loaded: {tool.name}")

        return tools

    except Exception as e:
        logger.error(f"Failed to load MCP tools: {e}")
        return []
