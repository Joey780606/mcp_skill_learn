"""Skills panel: dropdown of skill demos + Run button."""
import customtkinter as ctk
from typing import Callable
from app.skills.registry import SkillRegistry


class SkillPanel(ctk.CTkFrame):
    def __init__(self, parent, registry: SkillRegistry, on_run: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self._registry = registry
        self._on_run = on_run  # signature: on_run(entry, fn, done_cb)

        ctk.CTkLabel(
            self,
            text="Skills",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(12, 6))

        names = registry.names() or ["(no skills configured)"]
        self._var = ctk.StringVar(value=names[0])
        self._dropdown = ctk.CTkOptionMenu(
            self,
            variable=self._var,
            values=names,
            width=260,
        )
        self._dropdown.pack(padx=12, pady=4)

        self._btn = ctk.CTkButton(
            self,
            text="▶  Run",
            width=120,
            command=self._run,
        )
        self._btn.pack(pady=(6, 12))

    def _run(self) -> None:
        name = self._var.get()
        result = self._registry.get(name)
        if result is None:
            return
        entry, fn = result
        self._btn.configure(state="disabled", text="Running…")
        self._on_run(entry, fn, self._on_done)

    def _on_done(self) -> None:
        self._btn.configure(state="normal", text="▶  Run")

    def refresh(self) -> None:
        """Reload dropdown values from registry."""
        names = self._registry.names() or ["(no skills configured)"]
        self._dropdown.configure(values=names)
        self._var.set(names[0])
