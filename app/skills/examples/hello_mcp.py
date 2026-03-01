"""Skill: What is MCP? — a conceptual overview."""


def run() -> str:
    return """\
What is MCP (Model Context Protocol)?
======================================
MCP is an open standard created by Anthropic (2024) that defines
how AI applications connect with external tools and data sources.

Key concepts:
  Server    — exposes Tools, Resources, and Prompts to clients
  Client    — connects to servers and calls their tools
  Transport — stdio (local subprocess) or HTTP+SSE (remote)
  Tools     — callable functions the LLM can invoke
  Resources — data the LLM can read (files, DB rows, APIs)
  Prompts   — reusable prompt templates

Data flow:
  AI App (Client) ──► MCP Server ──► External Tool/Data
                   ◄──            ◄──

This app uses the official Python MCP SDK  →  pip install mcp
Learn more: https://modelcontextprotocol.io

How to add a new MCP server to this app:
  1. Add an entry to config/mcp_config.json
  2. Restart the app — the dropdown updates automatically!"""
