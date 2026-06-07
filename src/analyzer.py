import base64
import json
import re
from pathlib import Path

import anthropic

import config


def _encode_image(image_path: Path) -> tuple[str, str]:
    """Return (base64_data, media_type) for the given image file."""
    suffix = image_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    media_type = media_types.get(suffix, "image/jpeg")
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def analyze_render(image_path: Path) -> dict:
    """
    Send the render to Claude vision for analysis.
    Returns structured assessment dict.
    """
    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set in environment.")

    system_prompt = config.ANALYSIS_PROMPT.read_text()
    image_data, media_type = _encode_image(image_path)

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Analyze this architectural render and return your assessment as a JSON object exactly as specified in your instructions.",
                    },
                ],
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Extract JSON from the response (handles markdown code blocks)
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not json_match:
        raise ValueError(f"Claude did not return valid JSON. Response:\n{raw}")

    return json.loads(json_match.group())
