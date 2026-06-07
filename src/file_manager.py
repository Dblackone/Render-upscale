"""File I/O, session management, and image directory organisation."""

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

import config


def new_session_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]


def setup_session(image_path: Path, session_id: str) -> dict:
    """
    Copy input image to raw-renders, create WIP session folder.
    Returns session metadata dict.
    """
    # Copy to raw-renders
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_dest = config.RAW_DIR / image_path.name
    if not raw_dest.exists():
        shutil.copy2(image_path, raw_dest)

    # Create WIP session folder
    wip_folder = config.WIP_DIR / session_id
    wip_folder.mkdir(parents=True, exist_ok=True)

    session = {
        "session_id": session_id,
        "source_image": str(image_path),
        "raw_copy": str(raw_dest),
        "wip_folder": str(wip_folder),
        "created_at": datetime.now().isoformat(),
        "status": "analysing",
        "iterations": [],
    }
    _save_session(session)
    return session


def save_enhanced(session: dict, enhanced_path: Path, iteration: int = 1) -> Path:
    """Move enhanced image to enhanced-renders/<session_id>/."""
    dest_dir = config.ENHANCED_DIR / session["session_id"]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"enhanced_v{iteration}{enhanced_path.suffix}"
    shutil.copy2(enhanced_path, dest)
    session["iterations"].append({"version": iteration, "path": str(dest)})
    session["status"] = "enhanced"
    _save_session(session)
    return dest


def approve_final(session: dict, enhanced_path: Path) -> Path:
    """Copy approved image to final-deliverables/<session_id>/."""
    dest_dir = config.FINAL_DIR / session["session_id"]
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / ("final" + enhanced_path.suffix)
    shutil.copy2(enhanced_path, dest)
    session["status"] = "final"
    session["final_output"] = str(dest)
    _save_session(session)
    return dest


def _save_session(session: dict) -> None:
    wip_folder = Path(session["wip_folder"])
    wip_folder.mkdir(parents=True, exist_ok=True)
    (wip_folder / "session.json").write_text(json.dumps(session, indent=2))


def load_session(session_id: str) -> dict | None:
    path = config.WIP_DIR / session_id / "session.json"
    if path.exists():
        return json.loads(path.read_text())
    return None
