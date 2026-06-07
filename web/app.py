"""FastAPI web backend for the render enhancement system."""

import sys
import shutil
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

import config
from src import analyzer, assessor, file_manager, prompt_builder, generator

app = FastAPI(title="AI Render Enhancement", version="1.0.0")

app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")
app.mount("/images", StaticFiles(directory=str(config.IMAGES_DIR)), name="images")

_INDEX_HTML = (config.TEMPLATES_DIR / "index.html").read_text()


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=_INDEX_HTML)


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Accept an uploaded render, run analysis, return assessment + session ID."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        session_id = file_manager.new_session_id()
        session = file_manager.setup_session(tmp_path, session_id)

        analysis = analyzer.analyze_render(tmp_path)
        session["analysis"] = analysis
        file_manager._save_session(session)

        render_type = analysis.get("render_type", "exterior")
        questions = assessor.get_questions(render_type)
        assessment_text = assessor.format_assessment(analysis)

        return {
            "session_id": session_id,
            "render_type": render_type,
            "analysis": analysis,
            "assessment_text": assessment_text,
            "questions": questions,
        }
    finally:
        tmp_path.unlink(missing_ok=True)


@app.get("/assess/{session_id}")
async def get_assessment(session_id: str):
    """Return the stored assessment for a session."""
    session = file_manager.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "session_id": session_id,
        "analysis": session.get("analysis"),
        "status": session.get("status"),
    }


@app.post("/generate/{session_id}")
async def generate_image(
    session_id: str,
    time_of_day: str = Form(default=""),
    weather: str = Form(default=""),
    occupancy: str = Form(default=""),
    tone: str = Form(default=""),
    mood: str = Form(default=""),
    additional: str = Form(default=""),
):
    """Trigger DALL-E generation with user preferences."""
    session = file_manager.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    analysis = session.get("analysis", {})
    render_type = analysis.get("render_type", "exterior")

    user_answers = {k: v for k, v in {
        "time_of_day": time_of_day,
        "weather": weather,
        "occupancy": occupancy,
        "tone": tone,
        "mood": mood,
        "additional_instructions": additional,
    }.items() if v}

    prompt = prompt_builder.build_prompt(render_type, analysis, user_answers)
    session["prompt"] = prompt
    session["user_answers"] = user_answers
    file_manager._save_session(session)

    source_image = Path(session["raw_copy"])
    wip_folder = Path(session["wip_folder"])
    iteration = len(session.get("iterations", [])) + 1
    raw_output = wip_folder / f"enhanced_raw_v{iteration}{source_image.suffix}"

    try:
        enhanced_raw = generator.generate_enhanced(source_image, prompt, raw_output)
        saved = file_manager.save_enhanced(session, enhanced_raw, iteration)
        final = file_manager.approve_final(session, saved)

        # Return a web-accessible path
        relative = final.relative_to(config.IMAGES_DIR)
        return {
            "session_id": session_id,
            "result_url": f"/images/{relative}",
            "local_path": str(final),
            "iteration": iteration,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/result/{session_id}")
async def get_result(session_id: str):
    """Return the latest enhanced image for a session."""
    session = file_manager.load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    final = session.get("final_output")
    if final and Path(final).exists():
        return FileResponse(final)

    iterations = session.get("iterations", [])
    if iterations:
        last = Path(iterations[-1]["path"])
        if last.exists():
            return FileResponse(last)

    raise HTTPException(status_code=404, detail="No enhanced image available yet.")


@app.get("/health")
async def health():
    return {"status": "ok"}
