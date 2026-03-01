"""
Demo MCP server: time-server
Exposes a 'get_current_time' tool that returns the current date and time.
Run standalone: python servers/time_server.py
"""
from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("time-server")


@mcp.tool()
def get_current_time() -> str:
    """Returns the current date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    mcp.run()
