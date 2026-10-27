# Nano Banana MCP — Installation Guide

This guide covers configuring the Nano Banana 2 remote MCP server
(`https://mcp.pixa.com/mcp`) for use in Claude Code. No local package
install is required — the server runs remotely.

---

## Prerequisites

### Claude Code

Claude Code must be installed and running. The `.claude/settings.json`
file in this repository registers the MCP server at the project level —
no global configuration is needed.

### Network Access

The MCP server is hosted at `https://mcp.pixa.com/mcp`. Ensure outbound
HTTPS on port 443 is not blocked in your environment.

---

## Step 1 — Obtain a Pixa API Key

See [AUTHENTICATION.md](AUTHENTICATION.md) for the full key setup guide.
At minimum you need `PIXA_API_KEY` set in your environment before
Claude Code can connect.

---

## Step 2 — Configure Your Environment

Copy the environment variable template:

```bash
cp .env.example .env
```

Open `.env` and set your `PIXA_API_KEY`. See
[AUTHENTICATION.md](AUTHENTICATION.md) for how to obtain this key.

At minimum, your `.env` must contain:

```dotenv
PIXA_API_KEY=your_actual_pixa_key_here
```

---

## Step 3 — Open the Project in Claude Code

The project-level MCP configuration is already in place at
`.claude/settings.json`. When you open this project in Claude Code:

1. Claude Code detects `.claude/settings.json` automatically.
2. The `nanobanana` MCP server is registered.
3. The server starts on demand when you first call a Nano Banana tool.
4. Tools `generate_image` and `edit_image` become available.

**Verify MCP is active**: In Claude Code, run `/mcp` to list registered
servers. You should see `nanobanana` listed as active.

---

## Step 4 — Prepare Output Directory

The server writes enhanced renders to `./images/enhanced-renders/`. Create
this directory if it does not exist:

```bash
mkdir -p images/enhanced-renders
mkdir -p images/raw-renders
mkdir -p images/work-in-progress
mkdir -p images/final-deliverables
```

This matches the full directory structure described in the project README.

---

## Alternative: Cursor Configuration

To use the Pixa MCP server in Cursor, add to `.cursor/mcp.json` or via
Cursor Settings > MCP:

```json
{
  "mcpServers": {
    "nanobanana": {
      "type": "http",
      "url": "https://mcp.pixa.com/mcp",
      "headers": {
        "Authorization": "Bearer your_pixa_api_key_here"
      }
    }
  }
}
```

Do not commit this file if it contains a live key.

---

## Alternative: VS Code with MCP Extension

```json
{
  "mcp.servers": {
    "nanobanana": {
      "type": "http",
      "url": "https://mcp.pixa.com/mcp",
      "headers": {
        "Authorization": "Bearer ${env:PIXA_API_KEY}"
      }
    }
  }
}
```

---

## Alternative: Global Claude Code Configuration

To make the server available across all projects, add the same
`mcpServers` block to your global Claude Code settings at:

- macOS / Linux: `~/.claude/settings.json`
- Windows: `%APPDATA%\Claude\settings.json`

The project-level `.claude/settings.json` takes precedence if both are present.
