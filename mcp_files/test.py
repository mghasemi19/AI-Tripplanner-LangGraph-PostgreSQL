
import os
import asyncio
import shutil

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

# ==========================================
# 1. Environment configuration
# ==========================================

load_dotenv()

api_key = os.getenv("AVIATIONSTACK_API_KEY")

if not api_key:
    raise ValueError("Missing AVIATIONSTACK_API_KEY in .env")

if shutil.which("uvx") is None:
    raise RuntimeError(
        "uvx was not found. Install uv and check your PATH."
    )

# Preserve environment variables for subprocess
aviation_env = os.environ.copy()
aviation_env["AVIATION_STACK_API_KEY"] = api_key


# ==========================================
# 2. MCP client
# ==========================================

client = MultiServerMCPClient({
    "aviationstack": {
        "transport": "stdio",
        "command": "uvx",
        "args": ["aviationstack-mcp"],
        "env": aviation_env,
    }
})


# ==========================================
# 3. Cache available MCP tools
# ==========================================

aviation_tools = {}


async def initialize_aviation_tools():
    global aviation_tools

    if aviation_tools:
        return aviation_tools

    tools = await client.get_tools(
        server_name="aviationstack"
    )

    aviation_tools = {
        tool.name: tool
        for tool in tools
    }

    if not aviation_tools:
        raise RuntimeError(
            "AviationStack MCP returned no tools."
        )

    return aviation_tools


# ==========================================
# 4. Generic AviationStack tool caller
# ==========================================

async def aviation_mcp_call(
    tool_name: str,
    tool_args: dict | None = None
):
    tools = await initialize_aviation_tools()

    tool = tools.get(tool_name)

    if tool is None:
        available = ", ".join(sorted(tools.keys()))

        raise ValueError(
            f"Tool '{tool_name}' was not found. "
            f"Available tools: {available}"
        )

    result = await tool.ainvoke(tool_args or {})

    return result


# ==========================================
# 5. Main function
# ==========================================

async def main():

    tools = await initialize_aviation_tools()

    print("\nAvailable AviationStack tools:\n")

    for name, tool in tools.items():
        print(f"Tool: {name}")
        #print(f"Description: {tool.description}")
        print(f"Arguments: {tool.args}")
        print("-" * 50)

    # After inspecting the available tools, call one:
    result = await aviation_mcp_call(
        "list_airports",
        {"argument_name": "argument_value"}
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
