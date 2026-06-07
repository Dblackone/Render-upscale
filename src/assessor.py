"""Formats analyzer output into human-readable reports and generates clarification questions."""

QUESTIONS_BY_TYPE = {
    "exterior": [
        {
            "key": "time_of_day",
            "question": "Time of day?",
            "options": ["Golden hour (morning)", "Golden hour (evening)", "Midday sun", "Overcast / cloudy", "Blue hour / dusk", "Night"],
            "default": "Golden hour (evening)",
        },
        {
            "key": "weather",
            "question": "Weather conditions?",
            "options": ["Clear and sunny", "Partly cloudy", "Overcast / soft light", "After rain (wet surfaces)", "Dramatic stormy sky"],
            "default": "Partly cloudy",
        },
        {
            "key": "occupancy",
            "question": "Level of human activity?",
            "options": ["Busy / highly occupied", "Moderate activity", "A few people only", "Unoccupied"],
            "default": "Moderate activity",
        },
        {
            "key": "tone",
            "question": "Image tone / purpose?",
            "options": ["Luxury marketing", "Everyday realistic", "Competition / editorial", "Construction documentation"],
            "default": "Luxury marketing",
        },
    ],
    "interior": [
        {
            "key": "time_of_day",
            "question": "Lighting scenario?",
            "options": ["Bright daytime with sunlight", "Soft daytime / overcast", "Evening with artificial lighting", "Night — fully artificial"],
            "default": "Bright daytime with sunlight",
        },
        {
            "key": "occupancy",
            "question": "Level of occupancy?",
            "options": ["Occupied — people present", "Staged but empty", "Minimal props only"],
            "default": "Staged but empty",
        },
        {
            "key": "mood",
            "question": "Desired mood?",
            "options": ["Warm and inviting", "Crisp and minimal", "Dramatic and moody", "Bright and airy"],
            "default": "Warm and inviting",
        },
        {
            "key": "style",
            "question": "Interior design character?",
            "options": ["Luxury / high-end", "Contemporary / everyday", "Industrial / raw", "Hospitality / hotel"],
            "default": "Contemporary / everyday",
        },
    ],
    "landscape": [
        {
            "key": "vegetation_density",
            "question": "Vegetation density?",
            "options": ["Dense and lush", "Moderate planting", "Minimal / sparse planting", "Formal / clipped"],
            "default": "Dense and lush",
        },
        {
            "key": "climate",
            "question": "Climate zone / region?",
            "options": ["Temperate (UK / Northern Europe)", "Mediterranean", "Tropical / subtropical", "Arid / dry", "Northern / Scandinavian"],
            "default": "Temperate (UK / Northern Europe)",
        },
        {
            "key": "season",
            "question": "Season?",
            "options": ["Spring — fresh green growth", "Summer — full canopy", "Autumn — warm tones", "Winter — bare branches"],
            "default": "Summer — full canopy",
        },
        {
            "key": "occupancy",
            "question": "Occupied or empty?",
            "options": ["Occupied — people enjoying the space", "Empty — landscape only"],
            "default": "Occupied — people enjoying the space",
        },
    ],
    "urban": [
        {
            "key": "time_of_day",
            "question": "Time of day?",
            "options": ["Morning rush", "Midday — busy", "Late afternoon golden hour", "Evening / dusk", "Night — lit"],
            "default": "Late afternoon golden hour",
        },
        {
            "key": "activity_level",
            "question": "Street activity level?",
            "options": ["Very busy / vibrant", "Moderate activity", "Quiet / calm", "Empty / deserted"],
            "default": "Moderate activity",
        },
        {
            "key": "weather",
            "question": "Weather?",
            "options": ["Clear and sunny", "Partly cloudy", "Overcast", "After rain"],
            "default": "Partly cloudy",
        },
    ],
    "bim": [
        {
            "key": "purpose",
            "question": "Primary purpose of this image?",
            "options": ["Design review / client presentation", "Planning / approval submission", "Competition entry", "Marketing"],
            "default": "Design review / client presentation",
        },
        {
            "key": "time_of_day",
            "question": "Preferred lighting?",
            "options": ["Daytime — clear", "Daytime — overcast", "Golden hour", "No preference — maximize clarity"],
            "default": "Daytime — clear",
        },
        {
            "key": "occupancy",
            "question": "Include people?",
            "options": ["Yes — 3-5 people for scale", "Minimal — 1-2 only", "No people"],
            "default": "Yes — 3-5 people for scale",
        },
    ],
}


def format_assessment(analysis: dict) -> str:
    """Return a formatted Image Assessment string for display."""
    score = analysis.get("realism_score", "?")
    score_bar = "█" * int(score) + "░" * (10 - int(score))

    lines = [
        "━" * 60,
        "  IMAGE ASSESSMENT",
        "━" * 60,
        f"  Render Type   : {analysis.get('render_type', 'unknown').upper()}",
        f"  Quality        : {analysis.get('current_quality', '—')}",
        f"  Realism Score  : {score}/10  [{score_bar}]",
        "",
        "  STRENGTHS",
    ]
    for s in analysis.get("strengths", []):
        lines.append(f"  ✓  {s}")

    lines += ["", "  WEAKNESSES"]
    for w in analysis.get("weaknesses", []):
        lines.append(f"  ✗  {w}")

    lines += [
        "",
        "  ENHANCEMENT NOTES",
        f"  Lighting    : {analysis.get('lighting_notes', '—')}",
        f"  Materials   : {analysis.get('material_notes', '—')}",
        f"  Environment : {analysis.get('environment_notes', '—')}",
        f"  Vegetation  : {analysis.get('vegetation_notes', '—')}",
        f"  Entourage   : {analysis.get('entourage_notes', '—')}",
        f"  Atmosphere  : {analysis.get('atmosphere_notes', '—')}",
        "━" * 60,
    ]
    return "\n".join(lines)


def get_questions(render_type: str) -> list[dict]:
    """Return the list of clarification questions for this render type."""
    return QUESTIONS_BY_TYPE.get(render_type, QUESTIONS_BY_TYPE["exterior"])
