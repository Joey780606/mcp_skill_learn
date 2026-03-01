"""
MCP Skill Learn — Entry Point
Run from the project root: python main.py
"""
import asyncio
import os
import sys
import threading

# Ensure project root is on sys.path so 'app.*' imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from app.mcp.registry import MCPRegistry
from app.skills.registry import SkillRegistry
from app.ui.main_window import MainWindow


def main() -> None:
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # Load configs
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    mcp_registry = MCPRegistry.load(os.path.join(config_dir, "mcp_config.json"))
    skill_registry = SkillRegistry.load(os.path.join(config_dir, "skills_config.json"))

    # Create a dedicated asyncio event loop on a background daemon thread.
    # On Windows, ProactorEventLoop is required for subprocess support.
    if sys.platform == "win32":
        async_loop: asyncio.AbstractEventLoop = asyncio.ProactorEventLoop()
    else:
        async_loop = asyncio.new_event_loop()

    loop_thread = threading.Thread(
        target=async_loop.run_forever,
        name="asyncio-background",
        daemon=True,
    )
    loop_thread.start()

    # Launch the UI (blocks until the window is closed)
    app = MainWindow(
        async_loop=async_loop,
        mcp_registry=mcp_registry,
        skill_registry=skill_registry,
    )
    app.mainloop()

    # Gracefully stop the background event loop
    async_loop.call_soon_threadsafe(async_loop.stop)


if __name__ == "__main__":
    main()
