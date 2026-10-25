"""SnapTutor Flask app — image-to-tutoring powered by Gemma 4."""

import logging
import os

from flask import Flask, jsonify, render_template, request

from tutor import VALID_LEVELS, VALID_MODES, run_tutor

# ---------------------------------------------------------------------------
# App factory & config
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB upload cap

ALLOWED_MIME = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _allowed_file(filename: str) -> bool:
    """Check that the filename has an allowed image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/")
def index():
    """Serve the single-page app."""
    return render_template("index.html")


@app.get("/health")
def health():
    """Health check endpoint."""
    return jsonify(status="ok")


@app.post("/api/solve")
def solve():
    """Accept an image + options, run the tutor, and return Markdown JSON.

    Form fields:
        image  (file)  — required, must be PNG / JPG / WebP, max 8 MB
        mode   (str)   — 'explain' | 'hint' | 'quiz', default 'explain'
        level  (str)   — 'beginner' | 'intermediate' | 'exam', default 'intermediate'
        subject (str)  — optional free text (max 100 chars)
        question (str) — optional free text (max 500 chars)

    Returns:
        200  {"markdown": "..."}
        400  {"error": "..."}  — bad input
        413  {"error": "..."}  — image too large
        500  {"error": "..."}  — model / runtime error
        502  {"error": "..."}  — unexpected failure
    """
    # ── Validate image ───────────────────────────────────────────────
    file = request.files.get("image")
    if file is None or file.filename == "":
        return jsonify(error="Please choose an image first."), 400

    if not _allowed_file(file.filename):
        return jsonify(error="Unsupported file type. Use PNG, JPG, or WebP."), 400

    mime = file.mimetype
    if mime not in ALLOWED_MIME:
        return jsonify(error="Unsupported file type. Use PNG, JPG, or WebP."), 400

    image_bytes = file.read()
    if not image_bytes:
        return jsonify(error="The uploaded file is empty."), 400

    # ── Validate options ─────────────────────────────────────────────
    mode = request.form.get("mode", "explain")
    level = request.form.get("level", "intermediate")

    if mode not in VALID_MODES:
        return jsonify(error=f"Invalid mode '{mode}'. Use: {', '.join(sorted(VALID_MODES))}"), 400
    if level not in VALID_LEVELS:
        return jsonify(error=f"Invalid level '{level}'. Use: {', '.join(sorted(VALID_LEVELS))}"), 400

    subject = request.form.get("subject", "")
    question = request.form.get("question", "")

    # ── Call tutor ───────────────────────────────────────────────────
    try:
        result = run_tutor(
            image_bytes=image_bytes,
            mime=mime,
            mode=mode,
            level=level,
            subject=subject,
            question=question,
        )
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except RuntimeError as exc:
        logger.error("Tutor RuntimeError: %s", exc)
        return jsonify(error=str(exc)), 500
    except Exception:  # noqa: BLE001 — never leak stack traces to the browser
        logger.exception("Unexpected error in /api/solve")
        return jsonify(error="Something went wrong talking to the model. Please try again."), 502

    return jsonify(markdown=result)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------


@app.errorhandler(413)
def too_large(_err):
    """Handle uploads exceeding MAX_CONTENT_LENGTH."""
    return jsonify(error="Image is too large (max 8 MB)."), 413


@app.errorhandler(404)
def not_found(_err):
    """Handle unknown routes."""
    return jsonify(error="Not found."), 404


@app.errorhandler(405)
def method_not_allowed(_err):
    """Handle wrong HTTP methods."""
    return jsonify(error="Method not allowed."), 405


@app.errorhandler(500)
def internal_error(_err):
    """Catch-all for unhandled server errors."""
    logger.exception("Unhandled 500 error")
    return jsonify(error="Internal server error."), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    logger.info("Starting SnapTutor on port %d (debug=%s)", port, debug)
    app.run(host="0.0.0.0", port=port, debug=debug)
