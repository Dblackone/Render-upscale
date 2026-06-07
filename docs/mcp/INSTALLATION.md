# Nano Banana MCP — Installation Guide

This guide covers installing the `nanobanana-mcp-server` and configuring it
for use in Claude Code. Alternative configurations for Cursor and other MCP
clients are included at the end.

---

## Prerequisites

### Python and uv / uvx

`nanobanana-mcp-server` is a Python package. The recommended way to run it
is via `uvx`, which runs Python tools in isolated environments without a
permanent install.

**Install uv (includes uvx)**:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uvx --version
```

If you prefer not to use uvx, install the package directly:

```bash
pip install nanobanana-mcp-server
# or
uv pip install nanobanana-mcp-server
```

### Claude Code

Claude Code must be installed and running. The `.claude/settings.json`
file in this repository registers the MCP server at the project level,
so no global configuration is needed.

---

## Step 1 — Install uvx

Run the install command above for your platform. Confirm with:

```bash
uvx --version
# Expected output: uv x.x.x (or similar)
```

---

## Step 2 — Verify the MCP Server Works

Run a quick test to confirm the server can be launched:

```bash
uvx nanobanana-mcp-server@latest --help
```

If this completes without error, the server package is accessible. If you
see a network error, check your internet connection and pip registry access.

---

## Step 3 — Configure Your Environment

Copy the environment variable template:

```bash
cp .env.example .env
```

Open `.env` and set your `GEMINI_API_KEY`. See
[AUTHENTICATION.md](AUTHENTICATION.md) for how to obtain this key.

At minimum, your `.env` must contain:

```dotenv
GEMINI_API_KEY=your_actual_api_key_here
```

All other variables have sensible defaults in `.claude/settings.json`.

---

## Step 4 — Open the Project in Claude Code

The project-level MCP configuration is already in place at
`.claude/settings.json`. When you open this project in Claude Code:

1. Claude Code detects `.claude/settings.json` automatically.
2. The `nanobanana` MCP server is registered.
3. The server starts on demand when you first call a Nano Banana tool.
4. Tools `generate_image` and `edit_image` become available.

**Verify MCP is active**: In Claude Code, run `/mcp` to list registered
servers. You should see `nanobanana` listed as active.

---

## Step 5 — Prepare Output Directory

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

## Alternative: pip install (without uvx)

If uvx is unavailable in your environment:

```bash
pip install nanobanana-mcp-server
```

Then update `.claude/settings.json` to use `python -m` instead of `uvx`:

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "python",
      "args": ["-m", "nanobanana_mcp_server"],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}",
        "IMAGE_OUTPUT_DIR": "./images/enhanced-renders",
        "NANOBANANA_MODEL": "auto",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## Alternative: Cursor Configuration

To use this MCP server in Cursor, add the following to your Cursor MCP
settings (`.cursor/mcp.json` or via Cursor Settings > MCP):

```json
{
  "mcpServers": {
    "nanobanana": {
      "command": "uvx",
      "args": ["nanobanana-mcp-server@latest"],
      "env": {
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "IMAGE_OUTPUT_DIR": "./images/enhanced-renders",
        "NANOBANANA_MODEL": "auto"
      }
    }
  }
}
```

Note: Cursor may not support `${GEMINI_API_KEY}` shell variable
interpolation, so the API key may need to be entered directly. Do not
commit this file if it contains a live key.

---

## Alternative: VS Code with MCP Extension

If using VS Code with an MCP-compatible extension, add to your workspace
`.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "nanobanana": {
      "command": "uvx",
      "args": ["nanobanana-mcp-server@latest"],
      "env": {
        "GEMINI_API_KEY": "${env:GEMINI_API_KEY}",
        "IMAGE_OUTPUT_DIR": "${workspaceFolder}/images/enhanced-renders",
        "NANOBANANA_MODEL": "auto"
      }
    }
  }
}
```

---

## Alternative: Global Claude Code Configuration

To make the server available across all projects (not just this one),
add the same `mcpServers` block to your global Claude Code settings at:

- macOS / Linux: `~/.claude/settings.json`
- Windows: `%APPDATA%\Claude\settings.json`

The project-level `.claude/settings.json` takes precedence if both are
present.

---

## Updating the Server

Because the config uses `nanobanana-mcp-server@latest`, `uvx` always
fetches the latest version when the server starts. No manual update step
is needed. To pin to a specific version, change `@latest` to a version
tag such as `@0.4.2`.
