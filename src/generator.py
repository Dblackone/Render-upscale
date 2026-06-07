"""DALL-E 3 image generation via OpenAI images.edit endpoint."""

import base64
from pathlib import Path

import openai
from PIL import Image

import config


def _prepare_image(image_path: Path) -> Path:
    """
    Ensure image is PNG and ≤4MB as required by the images.edit endpoint.
    Returns path to a ready-to-use PNG (may be a converted temp file).
    """
    img = Image.open(image_path).convert("RGBA")

    # Resize to fit within 4096x4096 while preserving aspect ratio
    max_size = 4096
    if img.width > max_size or img.height > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)

    out_path = image_path.with_suffix(".png")
    img.save(out_path, "PNG", optimize=True)

    # If still too large, reduce quality iteratively
    size_limit = 4 * 1024 * 1024  # 4 MB
    scale = 0.9
    while out_path.stat().st_size > size_limit and scale > 0.3:
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        img.save(out_path, "PNG", optimize=True)
        scale *= 0.9

    return out_path


def generate_enhanced(
    image_path: Path,
    prompt: str,
    output_path: Path,
    size: str | None = None,
) -> Path:
    """
    Call DALL-E 3 edit to enhance the render.
    Returns the path to the saved output image.
    """
    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set in environment.")

    client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    chosen_size = size or config.DALLE_DEFAULT_SIZE

    prepared = _prepare_image(image_path)

    with open(prepared, "rb") as img_file:
        response = client.images.edit(
            model=config.DALLE_MODEL,
            image=img_file,
            prompt=prompt,
            n=1,
            size=chosen_size,
        )

    # The response contains a URL or b64_json — handle both
    result = response.data[0]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if hasattr(result, "b64_json") and result.b64_json:
        img_bytes = base64.b64decode(result.b64_json)
        output_path.write_bytes(img_bytes)
    elif hasattr(result, "url") and result.url:
        import urllib.request
        urllib.request.urlretrieve(result.url, output_path)
    else:
        raise RuntimeError("DALL-E response contained neither b64_json nor url.")

    # Clean up temp PNG if we created one
    if prepared != image_path and prepared.exists():
        prepared.unlink()

    return output_path
