"""Skill: call the echo tool on echo-server and display the MCP response."""
import asyncio
import sys
import os


def run() -> str:
    async def _inner() -> str:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        server_path = os.path.join(project_root, "servers", "echo_server.py")

        message = "Hello from mcp_skill_learn Skills!"
        print(f"Calling tool: echo")
        print(f"With argument: message = '{message}'\n")

        params = StdioServerParameters(command=sys.executable, args=[server_path])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("echo", {"message": message})

                lines = ["MCP tool response:"]
                for item in result.content:
                    if hasattr(item, "text"):
                        lines.append(f"  {item.text}")
                return "\n".join(lines)

    return asyncio.run(_inner())
