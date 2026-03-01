# Plan: mcp_skill_learn — Python Desktop App (Option A)

## Context
Build a desktop learning sandbox for MCP (Model Context Protocol) and Claude Code Skills.
Tech stack: Python 3.11+ · customtkinter · mcp SDK · asyncio.
The repo is brand new (only CLAUDE.md, README.md, LICENSE exist).

---

## Directory Structure

```
mcp_skill_learn/
├── main.py                          # Entry point
├── requirements.txt
├── PLAN.md                          # This file
├── config/
│   ├── mcp_config.json              # MCP server definitions (extensibility surface)
│   └── skills_config.json           # Skill function definitions
├── servers/
│   ├── echo_server.py               # Built-in demo MCP server (stdio)
│   └── time_server.py               # Built-in demo MCP server (stdio)
└── app/
    ├── ui/
    │   ├── main_window.py           # Root CTk window, layout orchestrator
    │   ├── mcp_panel.py             # MCP dropdown + Run button
    │   ├── skill_panel.py           # Skills dropdown + Run button
    │   └── output_panel.py          # Scrollable output text area
    ├── mcp/
    │   ├── client.py                # Async MCP ClientSession wrapper
    │   ├── runner.py                # Thread bridge: async MCP → Tkinter
    │   └── registry.py              # Loads mcp_config.json → MCPEntry list
    ├── skills/
    │   ├── registry.py              # Loads skills_config.json → SkillEntry list
    │   ├── runner.py                # Executes skills in ThreadPoolExecutor
    │   └── examples/
    │       ├── hello_mcp.py         # "What is MCP?" — text explanation
    │       ├── list_tools.py        # Connect to echo server, list tools
    │       └── echo_tool.py         # Call echo tool, show response
    └── config/
        └── loader.py                # Generic JSON config reader/validator
```

---

## UI Layout

```
┌────────────────────────────────────────────┐
│  MCP Panel           │  Skills Panel        │
│  [Dropdown ▼] [Run]  │  [Dropdown ▼] [Run] │
├────────────────────────────────────────────┤
│            Output Area  [Clear]             │
│  [HH:MM:SS] --- MCP: Echo Server ---       │
│  - echo: Returns the message you send      │
│  ─────────────────────────────────────     │
└────────────────────────────────────────────┘
```

---

## Threading / Async Architecture

**Problem:** MCP SDK is async; CustomTkinter is sync. Solution: Two-loop architecture.

```
MAIN THREAD                        BACKGROUND DAEMON THREAD
CustomTkinter mainloop()           asyncio loop (run_forever())
- All UI widget reads/writes       - All MCP ClientSession calls
- window.after(0, fn) for          - Subprocess lifecycle
  thread-safe UI updates           - Scheduled via
                                     run_coroutine_threadsafe()

                    THREADPOOLEXECUTOR (2 workers)
                    - Skill function execution
                    - Skills may call asyncio.run() safely
                      (they are NOT on the background loop thread)
```

`window.after(0, callback)` is the official Tkinter thread-safety mechanism used
for all cross-thread output panel updates.

---

## Key Data Flow: MCP Button Press

```
User clicks Run
  → MCPPanel reads dropdown → gets MCPEntry
  → Disables Run button
  → mcp_runner.run_mcp_entry(entry, async_loop, output_cb)
      → asyncio.run_coroutine_threadsafe(_execute(), async_loop)
          [background thread]
          → MCPClient.connect() → stdio_client spawns subprocess → handshake
          → session.list_tools() OR session.call_tool(...)
          → Format result
          → window.after(0, output_panel.append(result))
          → MCPClient.disconnect() → subprocess terminates
          → window.after(0, enable Run button)
```

## Key Data Flow: Skills Button Press

```
User clicks Run
  → SkillPanel reads dropdown → gets SkillEntry + callable fn
  → Disables Run button
  → ThreadPoolExecutor.submit(skill_runner.run_skill, fn, output_cb)
      [worker thread]
      → redirect_stdout(StringIO()) to capture print()
      → result = fn()
      → window.after(0, output_panel.append(stdout + result))
      → window.after(0, enable Run button)
```

---

## Config Schemas

### `config/mcp_config.json`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Dropdown display label |
| `description` | string | yes | Output section header |
| `command` | string | yes | Executable: `"python"`, `"node"`, `"npx"`, `"uvx"` |
| `args` | string[] | yes | Command arguments |
| `env` | object | no | Extra environment variables |
| `action` | enum | yes | `"list_tools"` \| `"list_resources"` \| `"list_prompts"` \| `"call_tool"` |
| `tool_name` | string | if call_tool | Tool to invoke |
| `tool_args` | object | if call_tool | Arguments for the tool |

### `config/skills_config.json`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Dropdown display label |
| `description` | string | yes | Output section header |
| `module` | string | yes | Fully-qualified Python module path |
| `function` | string | yes | Callable name inside the module |

Skill function contract: `def run() -> str:` — no params, may print, may call `asyncio.run()`.

---

## Extensibility Patterns

### Add a new MCP (no code needed)
Add an entry to `config/mcp_config.json`. The dropdown auto-populates on next launch.

External servers also work:
```json
{
  "name": "Filesystem MCP",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
  "action": "list_tools"
}
```

### Add a new Skill (minimal code)
1. Create `app/skills/examples/my_skill.py` with `def run() -> str: ...`
2. Add entry to `config/skills_config.json`

---

## Dependencies (`requirements.txt`)

```
customtkinter==5.2.2
mcp>=1.7.0
anyio>=4.0.0
httpx>=0.27.0
pydantic>=2.0.0
```

**Python ≥ 3.11 required.**

---

## Implementation Order

1. `requirements.txt`
2. `servers/echo_server.py` + `servers/time_server.py`
3. `config/mcp_config.json` + `config/skills_config.json`
4. `app/config/loader.py`
5. `app/mcp/registry.py` + `app/skills/registry.py`
6. `app/mcp/client.py`
7. `app/ui/output_panel.py`
8. `app/ui/main_window.py`
9. `app/ui/mcp_panel.py` + `app/ui/skill_panel.py`
10. `app/mcp/runner.py` + `app/skills/runner.py`
11. `app/skills/examples/hello_mcp.py`, `list_tools.py`, `echo_tool.py`
12. `main.py`

---

## Verification (End-to-End Test)

```bash
pip install -r requirements.txt
python main.py
```

1. App window opens with both dropdowns populated
2. Select "Echo Server — List Tools" → click Run → output shows tool list
3. Select "Echo Server — Call echo" → click Run → output shows: `Echo: Hello from mcp_skill_learn!`
4. Select "What is MCP?" skill → click Run → output shows explanation text
5. Click Clear → output area empties
6. Add new entry to `mcp_config.json`, restart → new item appears in MCP dropdown
