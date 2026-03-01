"""Thread bridge: submits async MCP work to the background event loop."""
import asyncio
from typing import Callable
from app.mcp.client import MCPClient
from app.mcp.registry import MCPEntry


def run_mcp_entry(
    entry: MCPEntry,
    async_loop: asyncio.AbstractEventLoop,
    output_cb: Callable[[str], None],
    done_cb: Callable[[], None],
) -> None:
    """Schedule an MCP operation on the background asyncio loop (non-blocking)."""
    client = MCPClient()

    async def _execute():
        try:
            result = await client.run_entry(entry)
            output_cb(result)
        except Exception as e:
            output_cb(f"ERROR ({type(e).__name__}): {e}")
        finally:
            done_cb()

    asyncio.run_coroutine_threadsafe(_execute(), async_loop)
