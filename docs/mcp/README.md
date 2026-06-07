# Nano Banana MCP — Render-upscale Integration

Nano Banana (Google Gemini image generation) is the primary AI image
generation engine powering this render enhancement lab. It is integrated
via the Model Context Protocol (MCP), making its tools directly available
inside Claude Code without leaving the editor.

---

## What is Nano Banana

Nano Banana is the popular name for Google's Gemini image generation model
family:

| Name | Model | Best For |
|---|---|---|
| Nano Banana Flash | Gemini 2.5 Flash Image | Fast iterations, draft reviews |
| Nano Banana 2 | Gemini 3.1 Flash Image | Standard production renders |
| Nano Banana Pro | Gemini Pro Image | 4K final deliverables, competition imagery |

The MCP server (`nanobanana-mcp-server`) wraps these models with smart
routing: when your prompt contains quality keywords like `4K`,
`professional`, `high-res`, `ultra`, `photorealistic`, or `architectural`,
the server automatically upgrades to the Pro model.

---

## MCP Server

**Package**: `nanobanana-mcp-server` (PyPI)
**Source**: `zhongweili/nanobanana-mcp-server`
**Install**: `uvx nanobanana-mcp-server@latest` (no persistent install needed)

This server was chosen over alternatives because it supports:

- 4K output — critical for professional architectural presentation
- Aspect ratio control — 16:9 for landscape renders, 21:9 for panoramas,
  1:1 for social, 2:3 for portrait elevations
- Smart model routing — quality keywords trigger Pro model automatically
- Configurable output directory — renders land directly in the project tree
- Vertex AI support — for enterprise and cloud-hosted workflows

---

## Available Tools

### `generate_image`

Generates a new image from a text prompt.

**Parameters**:
- `prompt` — Detailed description of the desired image
- `aspect_ratio` — Output ratio (e.g. `16:9`, `21:9`, `1:1`, `4:3`, `2:3`)
- `output_path` — Optional override for output file location

**When to use**: Creating reference images, sky replacements, material
references, entourage elements, or standalone concept renders.

### `edit_image`

Edits an existing image based on a text prompt. This is the primary tool
for render enhancement.

**Parameters**:
- `image_path` — Path to the input render (raw or WIP render)
- `prompt` — Description of enhancements to apply
- `aspect_ratio` — Preserve or change the output ratio
- `output_path` — Where to save the enhanced render

**When to use**: Applying all enhancements to existing renders — lighting
improvements, material upgrades, sky and environment enhancements, adding
entourage, improving realism. This is the core tool for the Step 5
Enhancement phase.

---

## Workflow Integration

The Render-upscale 7-step workflow maps directly to MCP tool calls:

```
Step 1 — Image Submission
  → User provides render file path (e.g. ./images/raw-renders/project.png)

Step 2 — Analysis
  → Claude Code reads the image and produces written analysis:
    lighting quality, material realism, environmental context,
    composition, identified weaknesses

Step 3 — Enhancement Strategy
  → Claude Code writes a structured enhancement plan:
    which elements to improve, in what order, target quality level

Step 4 — Clarification
  → Claude Code asks project-specific questions:
    time of day, weather, vegetation density, occupancy, mood

Step 5 — Enhancement  ← PRIMARY MCP CALL
  → edit_image(
       image_path="./images/raw-renders/project.png",
       prompt="[detailed enhancement prompt incorporating Steps 2-4]",
       aspect_ratio="16:9",
       output_path="./images/enhanced-renders/project_v1.png"
     )

Step 6 — Review
  → Claude Code evaluates the output against realism and design
    preservation standards. If not passing, loop back to Step 5
    with a revised prompt.

Step 7 — Final Delivery
  → Final image at ./images/enhanced-renders/project_final.png
  → Written enhancement summary
  → List of recommended further improvements
```

---

## Model Selection Guide

The `NANOBANANA_MODEL=auto` setting handles most cases. Use this reference
for manual overrides:

| Scenario | Recommended Model | Reason |
|---|---|---|
| Quick iteration / draft review | `flash` | Speed over quality |
| Standard production render | `nb2` | Balanced quality/speed |
| 4K final deliverable | `pro` | Maximum quality |
| Competition submission | `pro` | Maximum quality |
| Marketing / print material | `pro` | Maximum quality |
| BIM visualization review | `flash` or `nb2` | Internal review quality |
| Real estate listing | `nb2` or `pro` | Client-facing quality |

With `auto` mode, using phrases like "4K output", "professional quality",
"marketing-grade", "competition-level", or "ultra-photorealistic" in your
prompt automatically triggers Pro model routing.

---

## Architectural Visualization Examples

### Exterior Render Enhancement

```
edit_image(
  image_path="./images/raw-renders/residential_exterior_01.png",
  prompt="Transform this architectural render into an ultra-photorealistic
  exterior photograph. Enhance the golden hour lighting with warm directional
  sunlight casting long shadows. Upgrade concrete facade texture with realistic
  surface variation and micro-imperfections. Replace flat sky with layered
  cumulus clouds on deep blue. Add mature deciduous trees at correct scale
  with natural variation. Include 2-3 human figures in foreground for scale.
  Preserve all building geometry exactly. 4K professional quality output.",
  aspect_ratio="16:9",
  output_path="./images/enhanced-renders/residential_exterior_01_v1.png"
)
```

### Interior Render Enhancement

```
edit_image(
  image_path="./images/raw-renders/luxury_interior_01.png",
  prompt="Transform this interior render into ultra-photorealistic
  architectural photography. Enhance natural light entering through floor-to-
  ceiling windows with realistic caustics and volumetric shafts. Improve marble
  surfaces with authentic veining, depth, and reflections. Add realistic fabric
  texture to upholstery with natural wrinkle variation. Enhance ambient
  artificial lighting. Include tasteful decorative objects at correct scale.
  Maintain all interior geometry and layout. Professional quality.",
  aspect_ratio="4:3",
  output_path="./images/enhanced-renders/luxury_interior_01_v1.png"
)
```

### Landscape Render Enhancement

```
edit_image(
  image_path="./images/raw-renders/courtyard_landscape_01.png",
  prompt="Transform this landscape architecture render into a photorealistic
  site photograph. Enhance dappled shade light through tree canopy. Improve
  planting with varied species appropriate to Mediterranean climate and design
  language. Add water surface reflections with ripple realism. Enhance stone
  paving with natural weathering and moss at edges. Include people using the
  space naturally. Preserve all hardscape geometry. High-resolution output.",
  aspect_ratio="16:9",
  output_path="./images/enhanced-renders/courtyard_landscape_01_v1.png"
)
```

### BIM Visualization Enhancement

```
edit_image(
  image_path="./images/raw-renders/bim_export_01.png",
  prompt="Transform this BIM visualization into a professional presentation
  render. Add realistic materials to all surfaces — glass curtain wall,
  concrete structure, metal cladding. Enhance sky and environment. Add
  context vegetation and ground plane. Improve overall lighting to overcast
  professional daylight. Maintain all structural geometry exactly as modelled.
  Presentation quality output.",
  aspect_ratio="16:9",
  output_path="./images/enhanced-renders/bim_export_01_v1.png"
)
```

---

## Further Reading

- [Installation Guide](INSTALLATION.md) — How to install and configure the MCP server
- [Authentication Guide](AUTHENTICATION.md) — API key and Vertex AI setup
- [Troubleshooting Guide](TROUBLESHOOTING.md) — Common issues and fixes
