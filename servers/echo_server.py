"""
Demo MCP server: echo-server
Exposes a single 'echo' tool that returns the message you send.
Run standalone: python servers/echo_server.py
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("echo-server")


@mcp.tool()
def echo(message: str) -> str:
    """Returns the message you send"""
    return f"Echo: {message}"


if __name__ == "__main__":
    mcp.run()
