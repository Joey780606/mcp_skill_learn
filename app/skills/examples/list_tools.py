"""Skill: connect to echo-server via MCP and list its tools."""
import asyncio
import sys
import os


def run() -> str:
    async def _inner() -> str:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        # Resolve server path relative to project root
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        server_path = os.path.join(project_root, "servers", "echo_server.py")

        print(f"Connecting to echo-server at: {server_path}")
        print(f"Using Python: {sys.executable}\n")

        params = StdioServerParameters(command=sys.executable, args=[server_path])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()

                lines = [f"Found {len(result.tools)} tool(s) on echo-server:"]
                for tool in result.tools:
                    lines.append(f"  • {tool.name}: {tool.description}")
                    schema = tool.inputSchema or {}
                    for prop, info in schema.get("properties", {}).items():
                        req = prop in schema.get("required", [])
                        lines.append(
                            f"      param '{prop}' ({info.get('type', '?')})"
                            f"{' [required]' if req else ''}"
                        )
                return "\n".join(lines)

    return asyncio.run(_inner())
