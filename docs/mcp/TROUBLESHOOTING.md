# Nano Banana MCP — Troubleshooting Guide

---

## MCP Server Not Starting

**Symptom**: Claude Code shows `nanobanana` MCP server as inactive or
failed. Running a tool returns "MCP server unavailable".

**Causes and fixes**:

1. **uvx not found**
   ```
   Error: command not found: uvx
   ```
   Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   Then restart your terminal and Claude Code.

2. **uvx not on PATH visible to Claude Code**
   Claude Code may use a different PATH than your terminal. Check:
   ```bash
   which uvx
   echo $PATH
   ```
   If uvx is in a non-standard location (e.g. `~/.cargo/bin` or
   `~/.local/bin`), add it to your system PATH in `~/.bashrc` or
   `~/.zshrc`, then restart Claude Code fully.

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
Error: API_KEY_INVALID
Error: PERMISSION_DENIED: API key not valid
Error: 400 Bad Request: missing GEMINI_API_KEY
```

**Fixes**:

1. Check that `.env` exists and contains `GEMINI_API_KEY`:
   ```bash
   grep GEMINI_API_KEY .env
   ```

2. Confirm the key is not the placeholder value from `.env.example`:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here   ← THIS IS WRONG
   GEMINI_API_KEY=AIzaSyAbc123...            ← This is correct
   ```

3. Confirm Claude Code is loading your `.env`. Claude Code reads
   environment variables from the shell session it was launched from.
   Export the variable before launching:
   ```bash
   export GEMINI_API_KEY=$(grep GEMINI_API_KEY .env | cut -d= -f2)
   ```
   Or load `.env` into your shell: `source .env` then relaunch Claude Code.

4. Verify the key is active in Google AI Studio:
   https://aistudio.google.com/app/apikey

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

## uvx Not Found (Windows)

**Symptom**: `uvx` works in PowerShell but not when launched from Claude
Code or another GUI.

**Fix**: Add the uv bin directory to your system PATH (not just user PATH):

1. Open System Properties > Environment Variables.
2. Under System Variables, edit `Path`.
3. Add: `%USERPROFILE%\.local\bin` (or wherever uv was installed).
4. Restart Claude Code and any open terminals.

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

1. Check `nanobanana-mcp-server` issues:
   https://github.com/zhongweili/nanobanana-mcp-server/issues

2. Check Google AI Studio status:
   https://status.cloud.google.com/

3. Verify your Gemini API key is active and not expired:
   https://aistudio.google.com/app/apikey
