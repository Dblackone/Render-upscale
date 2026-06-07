import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

# API keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Models
CLAUDE_MODEL = "claude-opus-4-8"
DALLE_MODEL = "dall-e-3"

# DALL-E generation settings
DALLE_QUALITY = "hd"
DALLE_DEFAULT_SIZE = "1792x1024"
DALLE_SIZES = {
    "landscape": "1792x1024",
    "portrait": "1024x1792",
    "square": "1024x1024",
}

# Image directories
IMAGES_DIR = BASE_DIR / "images"
RAW_DIR = IMAGES_DIR / "raw-renders"
WIP_DIR = IMAGES_DIR / "work-in-progress"
ENHANCED_DIR = IMAGES_DIR / "enhanced-renders"
FINAL_DIR = IMAGES_DIR / "final-deliverables"

# Prompt directories
PROMPTS_DIR = BASE_DIR / "prompts"
ANALYSIS_PROMPT = PROMPTS_DIR / "analysis" / "system_prompt.txt"
ENHANCEMENT_BASE = PROMPTS_DIR / "enhancement" / "base.txt"
ENHANCEMENT_OVERLAYS = {
    "exterior": PROMPTS_DIR / "enhancement" / "exterior.txt",
    "interior": PROMPTS_DIR / "enhancement" / "interior.txt",
    "landscape": PROMPTS_DIR / "enhancement" / "landscape.txt",
    "urban": PROMPTS_DIR / "enhancement" / "urban.txt",
    "bim": PROMPTS_DIR / "enhancement" / "bim.txt",
}

# Web server
WEB_PORT = int(os.getenv("PORT", "8000"))
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"
