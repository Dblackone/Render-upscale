#!/usr/bin/env python3
"""render-enhance CLI — AI Render Optimization & Photorealistic Visualization System"""

import sys
from pathlib import Path

import click

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent))


@click.group()
def cli():
    """AI Render Optimization & Photorealistic Visualization System.

    Transform architectural renders into ultra-photorealistic images
    indistinguishable from professional photography.
    """


@cli.command()
@click.argument("image_path", type=click.Path(exists=True, path_type=Path))
def analyze(image_path: Path):
    """Analyze a render image and show the Image Assessment report.

    IMAGE_PATH: Path to the architectural render to analyze.
    """
    from src import analyzer, assessor

    click.echo(f"\n  Analyzing: {image_path.name}")
    try:
        result = analyzer.analyze_render(image_path)
        click.echo(assessor.format_assessment(result))
    except Exception as exc:
        click.echo(f"\n  Error: {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("image_path", type=click.Path(exists=True, path_type=Path))
def process(image_path: Path):
    """Run the full interactive 10-step enhancement workflow.

    IMAGE_PATH: Path to the architectural render to enhance.
    """
    from src.enhancer import run_workflow

    try:
        final = run_workflow(image_path)
        click.echo(f"\n  Done. Final deliverable: {final}")
    except KeyboardInterrupt:
        click.echo("\n  Interrupted.")
        sys.exit(0)
    except Exception as exc:
        click.echo(f"\n  Error: {exc}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--ext", default="jpg,jpeg,png,webp", help="Comma-separated file extensions to process.")
def batch(directory: Path, ext: str):
    """Process all render images in a directory non-interactively.

    DIRECTORY: Path to folder containing render images.
    """
    from src.enhancer import run_workflow

    extensions = {f".{e.strip().lower()}" for e in ext.split(",")}
    images = [p for p in directory.iterdir() if p.suffix.lower() in extensions]

    if not images:
        click.echo(f"  No images found in {directory} with extensions: {ext}")
        sys.exit(1)

    click.echo(f"\n  Found {len(images)} image(s) to process.")
    for i, img in enumerate(images, 1):
        click.echo(f"\n  [{i}/{len(images)}] Processing: {img.name}")
        try:
            final = run_workflow(img, non_interactive=True)
            click.echo(f"  Saved: {final}")
        except Exception as exc:
            click.echo(f"  Error processing {img.name}: {exc}", err=True)


@cli.command()
@click.option("--port", default=None, type=int, help="Port to run the web server on.")
@click.option("--host", default="0.0.0.0", help="Host to bind the web server to.")
def web(port: int | None, host: str):
    """Start the web interface for drag-and-drop image enhancement."""
    import uvicorn
    import config as cfg

    server_port = port or cfg.WEB_PORT
    click.echo(f"\n  Starting web server at http://{host}:{server_port}")
    uvicorn.run("web.app:app", host=host, port=server_port, reload=False)


if __name__ == "__main__":
    cli()
