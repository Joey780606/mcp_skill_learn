"""Async MCP client wrapper: connects, runs an action, disconnects."""
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.config.loader import get_project_root


def _resolve_command(command: str) -> str:
    """Replace 'python'/'python3' with the current interpreter for reliability."""
    if command in ("python", "python3"):
        return sys.executable
    return command


def _resolve_args(args: list) -> list:
    """Resolve relative .py paths against the project root."""
    root = get_project_root()
    resolved = []
    for arg in args:
        if not os.path.isabs(arg) and arg.endswith(".py"):
            candidate = os.path.join(root, arg)
            resolved.append(candidate if os.path.exists(candidate) else arg)
        else:
            resolved.append(arg)
    return resolved


class MCPClient:
    async def run_entry(self, entry) -> str:
        command = _resolve_command(entry.command)
        args = _resolve_args(entry.args)
        params = StdioServerParameters(
            command=command,
            args=args,
            env=entry.env if entry.env else None,
        )

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await self._dispatch(session, entry)

    async def _dispatch(self, session: ClientSession, entry) -> str:
        if entry.action == "list_tools":
            result = await session.list_tools()
            lines = [f"Tools on '{entry.name}':"]
            for tool in result.tools:
                lines.append(f"  • {tool.name}: {tool.description}")
            return "\n".join(lines) if len(lines) > 1 else "  (no tools found)"

        elif entry.action == "call_tool":
            result = await session.call_tool(entry.tool_name, entry.tool_args)
            texts = [c.text for c in result.content if hasattr(c, "text")]
            return "\n".join(texts) if texts else "(empty response)"

        elif entry.action == "list_resources":
            result = await session.list_resources()
            lines = [f"Resources on '{entry.name}':"]
            for res in result.resources:
                lines.append(f"  • {res.name}: {res.uri}")
            return "\n".join(lines) if len(lines) > 1 else "  (no resources found)"

        elif entry.action == "list_prompts":
            result = await session.list_prompts()
            lines = [f"Prompts on '{entry.name}':"]
            for p in result.prompts:
                lines.append(f"  • {p.name}: {p.description}")
            return "\n".join(lines) if len(lines) > 1 else "  (no prompts found)"

        else:
            return f"Unknown action: '{entry.action}'"
