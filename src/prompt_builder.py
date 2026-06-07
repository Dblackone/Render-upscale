"""Builds geometry-preserving DALL-E enhancement prompts from templates and user answers."""

from pathlib import Path

import config


GEOMETRY_LOCK = (
    "CRITICAL: DO NOT alter, modify, redesign, or change the architectural geometry, "
    "structural form, spatial layout, building massing, or design intent of the primary "
    "subject in any way. Preserve all geometry exactly as shown. Enhance ONLY photographic "
    "and environmental qualities."
)


def _load_template(path: Path) -> str:
    if path.exists():
        return path.read_text().strip()
    return ""


def _format_user_preferences(answers: dict) -> str:
    if not answers:
        return ""
    lines = ["USER PREFERENCES FOR THIS IMAGE:"]
    labels = {
        "time_of_day": "Time of day",
        "weather": "Weather",
        "occupancy": "Occupancy",
        "tone": "Tone / purpose",
        "mood": "Mood",
        "style": "Design style",
        "vegetation_density": "Vegetation density",
        "climate": "Climate zone",
        "season": "Season",
        "activity_level": "Activity level",
        "purpose": "Image purpose",
    }
    for key, value in answers.items():
        label = labels.get(key, key.replace("_", " ").title())
        lines.append(f"- {label}: {value}")
    return "\n".join(lines)


def build_prompt(render_type: str, analysis: dict, user_answers: dict) -> str:
    """
    Assemble the final DALL-E enhancement prompt.
    Combines: geometry lock + base directives + type overlay + user preferences.
    """
    base = _load_template(config.ENHANCEMENT_BASE)
    overlay_path = config.ENHANCEMENT_OVERLAYS.get(render_type)
    overlay = _load_template(overlay_path) if overlay_path else ""

    user_prefs = _format_user_preferences(user_answers)

    # Inject user preferences into base template
    filled_base = base.replace("{user_preferences}", user_prefs)

    sections = [GEOMETRY_LOCK, "", filled_base]
    if overlay:
        sections += ["", overlay]

    # Append key weaknesses from analysis as explicit fix directives
    weaknesses = analysis.get("weaknesses", [])
    if weaknesses:
        sections.append("\nSPECIFIC IMPROVEMENTS REQUIRED FOR THIS IMAGE:")
        for w in weaknesses[:5]:
            sections.append(f"- Fix: {w}")

    return "\n".join(sections)
