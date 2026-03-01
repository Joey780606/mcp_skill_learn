"""MCP server registry: loads mcp_config.json into typed MCPEntry objects."""
import sys
from dataclasses import dataclass, field
from app.config.loader import load_json_config


@dataclass
class MCPEntry:
    name: str
    description: str
    command: str
    args: list
    env: dict = field(default_factory=dict)
    action: str = "list_tools"
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)


class MCPRegistry:
    def __init__(self, entries: list):
        self.entries = entries

    @classmethod
    def load(cls, path: str) -> "MCPRegistry":
        data = load_json_config(path)
        entries = []
        for item in data.get("mcps", []):
            entries.append(MCPEntry(
                name=item["name"],
                description=item["description"],
                command=item["command"],
                args=item.get("args", []),
                env=item.get("env", {}),
                action=item.get("action", "list_tools"),
                tool_name=item.get("tool_name", ""),
                tool_args=item.get("tool_args", {}),
            ))
        return cls(entries)

    def names(self) -> list:
        return [e.name for e in self.entries]

    def get(self, name: str):
        return next((e for e in self.entries if e.name == name), None)
