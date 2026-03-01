## Project Goal
Learn MCP (Model Context Protocol) and Skills through a hands-on desktop application.

## Tech Stack
- **Python 3.11+**
- **customtkinter** — modern desktop UI
- **mcp** — official Anthropic MCP Python SDK
- **asyncio** — async runtime for MCP client calls

## Architecture
A desktop app with two panels side by side and a shared output area below:

```
┌─────────────────────────────────────────────┐
│  MCP Servers         │  Skills               │
│  [Dropdown ▼] [Run]  │  [Dropdown ▼] [Run]  │
├─────────────────────────────────────────────┤
│           Output Area          [Clear]       │
│  [HH:MM:SS]  <description>                  │
│  <result text>                               │
│  ────────────────────────────────────────   │
└─────────────────────────────────────────────┘
```

- **MCP panel**: selects a configured MCP server action and runs it via stdio transport
- **Skills panel**: selects a Python skill demo and runs it in a thread pool
- **Output area**: timestamped, scrollable, append-only log of all results

## Threading Model
- **Main thread**: CustomTkinter UI event loop
- **Background daemon thread**: persistent `asyncio` event loop for all MCP calls (`asyncio.ProactorEventLoop` on Windows)
- **ThreadPoolExecutor**: for skill function execution (skills may internally call `asyncio.run()`)
- Cross-thread UI updates use `window.after(0, callback)` — the official Tkinter thread-safety mechanism

## How to Run
```bash
pip install -r requirements.txt
python main.py
```
Must be run from the project root directory.

## Project Structure
```
mcp_skill_learn/
├── main.py                          # Entry point
├── requirements.txt
├── config/
│   ├── mcp_config.json              # MCP server definitions (add new MCPs here)
│   └── skills_config.json           # Skill definitions (add new Skills here)
├── servers/
│   ├── echo_server.py               # Demo MCP server: echo tool
│   └── time_server.py               # Demo MCP server: get_current_time tool
└── app/
    ├── config/loader.py             # JSON config loader + project root helper
    ├── mcp/
    │   ├── registry.py              # MCPEntry dataclass + MCPRegistry
    │   ├── client.py                # Async MCP ClientSession wrapper
    │   └── runner.py                # Thread bridge: schedules async MCP work
    ├── skills/
    │   ├── registry.py              # SkillEntry dataclass + SkillRegistry (dynamic import)
    │   ├── runner.py                # Runs skill fn in ThreadPoolExecutor, captures stdout
    │   └── examples/
    │       ├── hello_mcp.py         # "What is MCP?" explanation
    │       ├── list_tools.py        # Connect to echo-server, list tools
    │       └── echo_tool.py         # Call echo tool, show MCP response
    └── ui/
        ├── main_window.py           # Root CTk window, wires all panels
        ├── mcp_panel.py             # MCP dropdown + Run button
        ├── skill_panel.py           # Skills dropdown + Run button
        └── output_panel.py          # Scrollable output text area + Clear button
```

## Extending the App

### Add a new MCP server (no code required)
Add an entry to `config/mcp_config.json` and restart:
```json
{
  "name": "My Server — List Tools",
  "description": "Description shown in output",
  "command": "python",
  "args": ["servers/my_server.py"],
  "env": {},
  "action": "list_tools",
  "tool_name": "",
  "tool_args": {}
}
```
Supported `action` values: `"list_tools"` | `"call_tool"` | `"list_resources"` | `"list_prompts"`

External servers (npm/uvx) work too — just change `command` and `args`.

### Add a new Skill
1. Create `app/skills/examples/my_skill.py`:
```python
def run() -> str:
    print("optional stdout is captured too")
    return "result string shown in output"
```
2. Add an entry to `config/skills_config.json` and restart:
```json
{
  "name": "My Skill",
  "description": "Description shown in output",
  "module": "app.skills.examples.my_skill",
  "function": "run"
}
```
Skill contract: `def run() -> str` — no params, may `print()`, may call `asyncio.run()`.
