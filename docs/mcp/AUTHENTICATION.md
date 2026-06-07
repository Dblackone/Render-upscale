# Nano Banana MCP — Authentication Guide

The Nano Banana 2 MCP server is hosted remotely at `https://mcp.pixa.com/mcp`
and authenticates via a **Pixa API key** passed as a Bearer token.

---

## Step 1 — Obtain a Pixa API Key

1. Sign in or create an account at **https://pixa.com**
2. Navigate to your account settings or API section.
3. Generate an API key.
4. Copy the key — treat it like a password.

> Keep this key secure. Anyone with this key can make API calls on your account.

---

## Step 2 — Configure Your Environment

Copy the environment template and set your key:

```bash
cp .env.example .env
```

Open `.env` and set:

```dotenv
PIXA_API_KEY=your_actual_pixa_api_key_here
```

Claude Code reads `${PIXA_API_KEY}` from your shell environment and injects
it as the `Authorization: Bearer` header on every request to
`https://mcp.pixa.com/mcp`.

---

## Step 3 — Export the Key to Your Shell

Claude Code reads environment variables from the shell session it was
launched from. Before opening Claude Code, export the variable:

```bash
export PIXA_API_KEY=$(grep PIXA_API_KEY .env | cut -d= -f2)
```

Or load the whole `.env` file: `source .env`

---

## Step 4 — Never Commit Your Key

Confirm `.env` is protected by `.gitignore`:

```bash
grep "\.env" .gitignore
```

---

## Rotating Your API Key

If your Pixa API key is compromised:

1. Log in to **https://pixa.com** and revoke the key.
2. Generate a new key.
3. Update `.env` with the new value.
4. Restart Claude Code.

---

## Environment Variable Reference

| Variable | Required | Description |
|---|---|---|
| `PIXA_API_KEY` | Yes | Pixa account API key for `https://mcp.pixa.com/mcp` |
| `ANTHROPIC_API_KEY` | Yes | Claude vision analysis (core app) |
| `OPENAI_API_KEY` | Yes | DALL-E 3 generation (core app) |
