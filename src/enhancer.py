"""10-step workflow orchestrator for the interactive enhancement pipeline."""

import sys
from pathlib import Path

from src import analyzer, assessor, file_manager, generator, prompt_builder
import config


def _ask_question(q: dict) -> str:
    """Present a question with numbered options and return the user's answer."""
    print(f"\n  {q['question']}")
    options = q["options"]
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    default_idx = options.index(q["default"]) + 1
    while True:
        raw = input(f"  Enter choice [1-{len(options)}] (default {default_idx}): ").strip()
        if raw == "":
            return q["default"]
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  Please enter a number between 1 and {len(options)}.")


def _yes_no(prompt: str, default: bool = True) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        raw = input(prompt + suffix).strip().lower()
        if raw == "":
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False


def run_workflow(image_path: Path, non_interactive: bool = False, auto_answers: dict | None = None) -> Path:
    """
    Execute the full 10-step enhancement workflow.
    Returns path to the final deliverable image.

    non_interactive=True skips all prompts using defaults (for batch/web use).
    auto_answers can supply pre-filled question answers.
    """
    # ── Step 1: Analyse ──────────────────────────────────────────────────────
    print("\n  [1/10] Analysing image with Claude vision...")
    session_id = file_manager.new_session_id()
    session = file_manager.setup_session(image_path, session_id)

    analysis = analyzer.analyze_render(image_path)
    session["analysis"] = analysis
    file_manager._save_session(session)
    render_type = analysis.get("render_type", "exterior")

    # ── Step 2: Present Assessment ───────────────────────────────────────────
    print("\n  [2/10] Image Assessment")
    print(assessor.format_assessment(analysis))

    # ── Step 3: Project-specific questions ───────────────────────────────────
    print("\n  [3/10] Project-specific clarification")
    questions = assessor.get_questions(render_type)
    user_answers: dict = auto_answers or {}

    if not non_interactive:
        for q in questions:
            if q["key"] not in user_answers:
                user_answers[q["key"]] = _ask_question(q)
    else:
        for q in questions:
            if q["key"] not in user_answers:
                user_answers[q["key"]] = q["default"]

    session["user_answers"] = user_answers
    file_manager._save_session(session)

    # ── Step 4: Additional free-text instructions ─────────────────────────────
    additional = ""
    if not non_interactive:
        print("\n  [4/10] Additional instructions")
        additional = input("  Any additional instructions for this image? (press Enter to skip): ").strip()

    # ── Step 5: User approval ─────────────────────────────────────────────────
    if not non_interactive:
        print("\n  [5/10] Approve enhancement plan")
        print(f"  Render type : {render_type.upper()}")
        print(f"  Preferences : {user_answers}")
        if additional:
            print(f"  Extra notes : {additional}")
        if not _yes_no("\n  Proceed with generation?"):
            print("  Cancelled.")
            sys.exit(0)

    # ── Step 6: Build prompt ──────────────────────────────────────────────────
    print("\n  [6/10] Building enhancement prompt...")
    if additional:
        user_answers["additional_instructions"] = additional
    prompt = prompt_builder.build_prompt(render_type, analysis, user_answers)
    session["prompt"] = prompt
    file_manager._save_session(session)

    # ── Step 7: Generate ──────────────────────────────────────────────────────
    print("\n  [7/10] Generating enhanced image with DALL-E 3...")
    wip_folder = Path(session["wip_folder"])
    raw_output = wip_folder / ("enhanced_raw" + image_path.suffix)
    enhanced_raw = generator.generate_enhanced(image_path, prompt, raw_output)

    # ── Step 8: Save to enhanced-renders ─────────────────────────────────────
    print("\n  [8/10] Saving enhanced image...")
    iteration = len(session.get("iterations", [])) + 1
    saved = file_manager.save_enhanced(session, enhanced_raw, iteration)
    print(f"  Saved: {saved}")

    # ── Step 9: Review and iterate ────────────────────────────────────────────
    if not non_interactive:
        print(f"\n  [9/10] Review result at:\n  {saved}")
        while not _yes_no("\n  Approve this result and save as final deliverable?", default=True):
            refine = input("  Describe what to change (or press Enter to regenerate as-is): ").strip()
            if refine:
                user_answers["refinement_notes"] = refine
                prompt = prompt_builder.build_prompt(render_type, analysis, user_answers)
                session["prompt"] = prompt

            print("\n  Regenerating...")
            raw_output2 = wip_folder / f"enhanced_raw_v{iteration + 1}{image_path.suffix}"
            enhanced_raw = generator.generate_enhanced(image_path, prompt, raw_output2)
            iteration += 1
            saved = file_manager.save_enhanced(session, enhanced_raw, iteration)
            print(f"  New result: {saved}")

    # ── Step 10: Final deliverable ────────────────────────────────────────────
    final = file_manager.approve_final(session, saved)
    print(f"\n  [10/10] Final deliverable saved:\n  {final}")
    return final
