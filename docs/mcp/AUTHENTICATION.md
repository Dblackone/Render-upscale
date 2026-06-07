# Nano Banana MCP — Authentication Guide

Two authentication methods are supported:

| Method | Use Case |
|---|---|
| Gemini API Key | Standard use, individual developers, small teams |
| Vertex AI | Enterprise, cloud workflows, GCP-integrated pipelines |

The default and recommended method is **Gemini API Key**.

---

## Method 1: Gemini API Key (Recommended)

### Step 1 — Create a Google Account

You need a Google account to access Google AI Studio. If you already have
one (Gmail, Google Workspace), skip this step.

### Step 2 — Open Google AI Studio

Navigate to: **https://aistudio.google.com/app/apikey**

Sign in with your Google account.

### Step 3 — Generate an API Key

1. Click **Create API key**.
2. Select an existing Google Cloud project, or click **Create new project**
   and follow the prompt.
3. Click **Create API key in existing project** (or new project).
4. Copy the generated key — it will look like `AIzaSy...` (39 characters).

> Keep this key secure. Anyone with this key can make API calls billed
> to your account.

### Step 4 — Configure Your Environment

Open your `.env` file (copied from `.env.example`) and set:

```dotenv
GEMINI_API_KEY=AIzaSyYourActualKeyHere
NANOBANANA_AUTH_METHOD=api_key
```

### Step 5 — Never Commit Your Key

Ensure `.env` is listed in `.gitignore`. To verify:

```bash
grep "\.env" .gitignore
```

If `.env` is not listed, add it:

```
.env
*.env
```

### Free Tier and Quotas

Google AI Studio provides a free tier with rate limits:
- Gemini 2.5 Flash: 15 requests/minute, 1500 requests/day (free tier)
- Gemini Pro: lower free tier limits; billing may be required for high volume

For production render workloads, enable billing on your Google Cloud project
to avoid hitting rate limits. See the Pricing section in Google AI Studio.

---

## Method 2: Vertex AI (Enterprise)

Use Vertex AI if:
- You are on a Google Cloud enterprise contract
- You need higher rate limits or SLA guarantees
- Your organisation manages GCP projects centrally
- You are running automated batch render pipelines

### Step 1 — Set Up a Google Cloud Project

1. Go to **https://console.cloud.google.com/**
2. Create or select an existing GCP project.
3. Enable the **Vertex AI API**: Navigation > APIs & Services > Enable APIs
   > search for "Vertex AI API" > Enable.

### Step 2 — Install Google Cloud CLI

```bash
# macOS (Homebrew)
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Windows: download installer from https://cloud.google.com/sdk/docs/install
```

Verify: `gcloud --version`

### Step 3 — Authenticate

```bash
gcloud auth login
gcloud auth application-default login
```

The second command creates Application Default Credentials (ADC), which
`nanobanana-mcp-server` uses automatically when `NANOBANANA_AUTH_METHOD=vertex`.

### Step 4 — Configure Your Environment

```dotenv
NANOBANANA_AUTH_METHOD=vertex
GCP_PROJECT_ID=your-gcp-project-id
GCP_REGION=us-central1
# Leave GEMINI_API_KEY blank when using Vertex AI
```

Supported regions for Vertex AI image generation include:
- `us-central1` (Iowa) — recommended for lowest latency from North America
- `europe-west1` (Belgium) — recommended for EU data residency
- `asia-east1` (Taiwan)

Check the Vertex AI documentation for current regional availability.

### Step 5 — Verify Vertex AI Access

```bash
gcloud projects describe your-gcp-project-id
```

If this returns project metadata, your credentials are working.

---

## Rotating Your API Key

If your Gemini API key is compromised:

1. Go to **https://aistudio.google.com/app/apikey**
2. Delete the compromised key.
3. Create a new key.
4. Update `.env` with the new key.
5. Restart Claude Code to pick up the new value.

For Vertex AI, rotate credentials via `gcloud auth revoke` and
re-authenticate.

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes (api_key mode) | — | Google AI Studio API key |
| `NANOBANANA_AUTH_METHOD` | No | `api_key` | Auth method: `api_key` or `vertex` |
| `GCP_PROJECT_ID` | Yes (vertex mode) | — | Google Cloud project ID |
| `GCP_REGION` | No | `us-central1` | Vertex AI region |
