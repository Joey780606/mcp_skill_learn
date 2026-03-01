"""Scrollable output text area."""
import customtkinter as ctk
from datetime import datetime


class OutputPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Header row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=8, pady=(8, 0))
        ctk.CTkLabel(
            header_row,
            text="Output",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(
            header_row,
            text="Clear",
            width=60,
            height=28,
            command=self.clear,
        ).pack(side="right")

        # Scrollable text area
        self._textbox = ctk.CTkTextbox(
            self,
            state="disabled",
            wrap="word",
            font=ctk.CTkFont(family="Courier New", size=12),
        )
        self._textbox.pack(fill="both", expand=True, padx=8, pady=(4, 8))

    def append(self, header: str, text: str) -> None:
        """Thread-safe append — must be called from the Tkinter main thread."""
        ts = datetime.now().strftime("%H:%M:%S")
        divider = "─" * 52
        content = f"[{ts}]  {header}\n{text}\n{divider}\n\n"
        self._textbox.configure(state="normal")
        self._textbox.insert("end", content)
        self._textbox.configure(state="disabled")
        self._textbox.see("end")

    def clear(self) -> None:
        self._textbox.configure(state="normal")
        self._textbox.delete("1.0", "end")
        self._textbox.configure(state="disabled")
