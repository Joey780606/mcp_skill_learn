"""Skills registry: loads skills_config.json and dynamically imports skill functions."""
import importlib
import sys
from dataclasses import dataclass
from app.config.loader import load_json_config


@dataclass
class SkillEntry:
    name: str
    description: str
    module: str
    function: str


class SkillRegistry:
    def __init__(self, entries: list):
        # List of (SkillEntry, callable) tuples
        self._entries = entries

    @classmethod
    def load(cls, path: str) -> "SkillRegistry":
        data = load_json_config(path)
        entries = []
        for item in data.get("skills", []):
            entry = SkillEntry(
                name=item["name"],
                description=item["description"],
                module=item["module"],
                function=item["function"],
            )
            try:
                mod = importlib.import_module(entry.module)
                fn = getattr(mod, entry.function)
                entries.append((entry, fn))
            except (ImportError, AttributeError) as e:
                print(f"Warning: could not load skill '{entry.name}': {e}", file=sys.stderr)
        return cls(entries)

    def names(self) -> list:
        return [e.name for e, _ in self._entries]

    def get(self, name: str):
        """Returns (SkillEntry, callable) or None."""
        return next(((e, fn) for e, fn in self._entries if e.name == name), None)
