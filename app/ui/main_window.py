"""Root application window: assembles all panels and wires callbacks."""
import asyncio
import customtkinter as ctk
from app.mcp.registry import MCPRegistry
from app.skills.registry import SkillRegistry
from app.ui.mcp_panel import MCPPanel
from app.ui.skill_panel import SkillPanel
from app.ui.output_panel import OutputPanel
from app.mcp.runner import run_mcp_entry
from app.skills.runner import run_skill


class MainWindow(ctk.CTk):
    def __init__(
        self,
        async_loop: asyncio.AbstractEventLoop,
        mcp_registry: MCPRegistry,
        skill_registry: SkillRegistry,
    ):
        super().__init__()
        self._loop = async_loop

        self.title("MCP Skill Learn")
        self.geometry("860x580")
        self.minsize(700, 480)

        self._build_ui(mcp_registry, skill_registry)

    def _build_ui(self, mcp_registry: MCPRegistry, skill_registry: SkillRegistry) -> None:
        # Top row: two panels side by side
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=(10, 4))

        self._mcp_panel = MCPPanel(
            top_frame,
            registry=mcp_registry,
            on_run=self._on_mcp_run,
        )
        self._mcp_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self._skill_panel = SkillPanel(
            top_frame,
            registry=skill_registry,
            on_run=self._on_skill_run,
        )
        self._skill_panel.pack(side="left", fill="both", expand=True, padx=(5, 0))

        # Bottom: output panel (takes remaining space)
        self._output = OutputPanel(self)
        self._output.pack(fill="both", expand=True, padx=10, pady=(4, 10))

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _append_output(self, header: str, text: str) -> None:
        """Thread-safe: schedule output panel update on the Tkinter main thread."""
        self.after(0, lambda: self._output.append(header, text))

    def _on_mcp_run(self, entry, panel_done_cb) -> None:
        run_mcp_entry(
            entry=entry,
            async_loop=self._loop,
            output_cb=lambda text: self._append_output(entry.description, text),
            done_cb=lambda: self.after(0, panel_done_cb),
        )

    def _on_skill_run(self, entry, fn, panel_done_cb) -> None:
        run_skill(
            fn=fn,
            output_cb=lambda text: self._append_output(entry.description, text),
            done_cb=lambda: self.after(0, panel_done_cb),
        )
