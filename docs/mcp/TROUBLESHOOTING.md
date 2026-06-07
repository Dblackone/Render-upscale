# Nano Banana MCP — Troubleshooting Guide

---

## MCP Server Not Starting

**Symptom**: Claude Code shows `nanobanana` MCP server as inactive or
failed. Running a tool returns "MCP server unavailable".

**Causes and fixes**:

1. **No network access to mcp.pixa.com**
   The server is remote — confirm outbound HTTPS is not blocked:
   ```bash
   curl -I https://mcp.pixa.com/mcp
   ```
   A `401 Unauthorized` response means the host is reachable (key issue,
   not network). A timeout or `connection refused` means a firewall or
   proxy is blocking the request.

2. **PIXA_API_KEY not in environment**
   Claude Code reads env vars from the shell it was launched from. Export
   the key before opening Claude Code:
   ```bash
   export PIXA_API_KEY=your_key_here
   ```

3. **settings.json syntax error**
   Validate the JSON:
   ```bash
   python3 -m json.tool .claude/settings.json
   ```
   Fix any syntax errors reported.

---

## Missing or Invalid API Key

**Symptom**: Tool calls fail with authentication errors.

```
Error: 401 Unauthorized
Error: 403 Forbidden
Error: Missing or invalid Authorization header
```

**Fixes**:

1. Check that `.env` exists and contains `PIXA_API_KEY`:
   ```bash
   grep PIXA_API_KEY .env
   ```

2. Confirm the key is not the placeholder from `.env.example`:
   ```
   PIXA_API_KEY=your_pixa_api_key_here   ← THIS IS WRONG
   PIXA_API_KEY=px_abc123...             ← This is correct
   ```

3. Export the variable before launching Claude Code:
   ```bash
   export PIXA_API_KEY=$(grep PIXA_API_KEY .env | cut -d= -f2)
   ```
   Or load your entire `.env`: `source .env` then relaunch Claude Code.

4. Verify the key is active in your Pixa account dashboard at
   https://pixa.com

---

## Model Not Found

**Symptom**:
```
Error: Model not found: gemini-nano-banana-pro
Error: 404 Model gemini/flash-image not found
```

**Fixes**:

1. Check your `NANOBANANA_MODEL` value in `.env`:
   ```
   NANOBANANA_MODEL=auto    ← Valid
   NANOBANANA_MODEL=flash   ← Valid
   NANOBANANA_MODEL=nb2     ← Valid
   NANOBANANA_MODEL=pro     ← Valid
   NANOBANANA_MODEL=genius  ← INVALID — will cause this error
   ```

2. Reset to safe default: `NANOBANANA_MODEL=auto`

3. If using Vertex AI, confirm the model is available in your selected
   `GCP_REGION`. Not all models are available in all regions. Try
   `GCP_REGION=us-central1` as a fallback.

---

## Output Directory Permissions

**Symptom**:
```
Error: Permission denied: ./images/enhanced-renders/output.png
Error: FileNotFoundError: [Errno 2] No such file or directory: './images/enhanced-renders/'
```

**Fixes**:

1. Create the output directory:
   ```bash
   mkdir -p images/enhanced-renders
   ```

2. Check write permissions:
   ```bash
   ls -la images/
   touch images/enhanced-renders/test.txt && rm images/enhanced-renders/test.txt
   ```
   If the touch fails, fix permissions: `chmod 755 images/enhanced-renders`

3. If `IMAGE_OUTPUT_DIR` is set to an absolute path, confirm that path
   exists and is writable.

4. On Windows, ensure the path uses forward slashes or is properly escaped
   in the config.

---

## Rate Limit Errors

**Symptom**:
```
Error: 429 RESOURCE_EXHAUSTED: Quota exceeded
Error: Too many requests
```

**Fixes**:

1. **Free tier limits**: Gemini API free tier is limited to 15 requests/
   minute and 1500/day. Space out your enhancement calls.

2. **Enable billing**: For production workloads, enable billing on your
   Google Cloud project in the Google AI Studio dashboard. Paid tiers have
   significantly higher limits.

3. **Switch to flash model temporarily**:
   ```dotenv
   NANOBANANA_MODEL=flash
   ```
   Flash has higher free tier rate limits than Pro.

4. **Use Vertex AI**: For enterprise workloads, Vertex AI provides
   dedicated quota allocation with higher limits and SLA guarantees.

---

## Image Size / Format Errors

**Symptom**:
```
Error: Image too large: maximum input size is 20MB
Error: Unsupported image format: .tiff
Error: Image dimensions exceed maximum: 8192x8192
```

**Fixes**:

1. **File size**: Compress your input render to under 20MB before
   processing. For architectural renders, JPEG at 85% quality is usually
   sufficient for the input:
   ```bash
   # Using ImageMagick
   convert input_render.png -quality 85 -resize "4096x4096>" input_compressed.jpg
   ```

2. **Format**: Convert to PNG or JPEG before passing to the MCP server:
   ```bash
   convert render.tiff render.png
   ```
   Supported formats: PNG, JPEG, WEBP.

3. **Dimensions**: If the input exceeds 8192px on any side, resize it:
   ```bash
   convert render.png -resize "4096x4096>" render_resized.png
   ```

---

## Enhanced Render Looks Different from Original

**Symptom**: The model has changed building geometry, removed architectural
elements, or substantially redesigned parts of the scene.

**This is not an error — this is a prompting issue.**

The Golden Rule of this project is: preserve primary geometry.

**Fix**: Add explicit preservation instructions to your prompt:

```
...Preserve all building geometry exactly as shown. Do not alter
the massing, facade composition, window positions, structural form,
or any architectural elements. Enhance realism only — do not redesign.
```

If the issue persists, switch to a more conservative prompt that focuses
on single enhancement categories (lighting only, materials only) rather
than full enhancement in one pass. Use iterative enhancement via the
work-in-progress workflow.

---

## LOG_LEVEL=DEBUG for Diagnosis

When investigating an issue, enable debug logging to see all MCP
communications:

```dotenv
LOG_LEVEL=DEBUG
```

Then check the MCP server output in Claude Code's developer tools or
terminal. Debug logs show the exact API calls being made, model selected,
prompt sent, and response received.

Reset to `LOG_LEVEL=INFO` after diagnosis.

---

## Still Stuck?

1. Check Pixa status: https://pixa.com

2. Verify your Pixa API key is active in your account dashboard.

3. File an issue or contact Pixa support if the server endpoint is down.
