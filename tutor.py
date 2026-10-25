"""Core tutoring logic: loads the SnapTutor skill and calls Gemma 4 via the Gemini API."""

import logging
import mimetypes
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")
SKILL_PATH = Path(__file__).parent / "skills" / "snaptutor" / "SKILL.md"
TIMEOUT_SECONDS = int(os.getenv("MODEL_TIMEOUT", "120"))

VALID_MODES = {"explain", "hint", "quiz"}
VALID_LEVELS = {"beginner", "intermediate", "exam"}

MAX_SUBJECT_LEN = 100
MAX_QUESTION_LEN = 500

# ---------------------------------------------------------------------------
# Client singleton
# ---------------------------------------------------------------------------

_client = None


def get_client() -> genai.Client:
    """Create the API client lazily so the app can start without a key and
    show a clear error only when a request is actually made."""
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _client = genai.Client(api_key=key)
    return _client


def reset_client() -> None:
    """Reset the cached client (useful for testing)."""
    global _client
    _client = None


# ---------------------------------------------------------------------------
# Skill loading
# ---------------------------------------------------------------------------


def load_skill(path: Path | None = None) -> str:
    """Read SKILL.md and strip the YAML frontmatter.

    The file is re-read on every call so edits during development take
    effect instantly without restarting the server.
    """
    p = path or SKILL_PATH
    if not p.exists():
        raise FileNotFoundError(f"Skill file not found: {p}")
    text = p.read_text(encoding="utf-8")
    # Strip the YAML frontmatter block (--- ... ---)
    stripped = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    return stripped.strip()


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

MODE_INSTRUCTIONS = {
    "explain": "Respond in **explain** mode: provide a full step-by-step solution.",
    "hint": "Respond in **hint** mode: give exactly 3 progressive hints, do NOT reveal the answer.",
    "quiz": "Respond in **quiz** mode: generate 3 practice questions (easy, medium, hard) with hidden answers.",
}


def build_prompt(
    mode: str,
    level: str,
    subject: str = "",
    question: str = "",
) -> str:
    """Assemble the full prompt: skill text → mode → level → optional context."""
    parts = [
        "You must follow this tutoring skill exactly:\n",
        load_skill(),
        "\n---\n",
        "**Student request:**\n",
        MODE_INSTRUCTIONS.get(mode, MODE_INSTRUCTIONS["explain"]),
        f"\n- Difficulty level: **{level}**",
    ]
    if subject:
        parts.append(f"\n- Subject area: {subject}")
    if question:
        parts.append(f"\n- The student also asks: {question}")
    parts.append("\n\nLook at the attached image and respond now in the requested mode.")
    return "".join(parts)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_tutor(
    image_bytes: bytes,
    mime: str,
    mode: str = "explain",
    level: str = "intermediate",
    subject: str = "",
    question: str = "",
) -> str:
    """Send the image plus the skill-driven prompt to Gemma 4 and return Markdown text.

    Raises:
        ValueError: for bad inputs (mode, level, empty image)
        RuntimeError: for API / model errors
    """
    # ── Input validation ─────────────────────────────────────────────
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {sorted(VALID_MODES)}, got '{mode}'")
    if level not in VALID_LEVELS:
        raise ValueError(f"level must be one of {sorted(VALID_LEVELS)}, got '{level}'")
    if not image_bytes:
        raise ValueError("image_bytes must not be empty")

    # Truncate optional fields to safe lengths
    subject = subject.strip()[:MAX_SUBJECT_LEN]
    question = question.strip()[:MAX_QUESTION_LEN]

    # ── Build prompt & contents ──────────────────────────────────────
    prompt_text = build_prompt(mode, level, subject, question)
    contents = [
        types.Part.from_bytes(data=image_bytes, mime_type=mime),
        prompt_text,
    ]

    # ── Call the model ───────────────────────────────────────────────
    logger.info("Calling model=%s mode=%s level=%s", MODEL, mode, level)
    start = time.time()

    try:
        response = get_client().models.generate_content(
            model=MODEL,
            contents=contents,
        )
    except Exception as exc:
        elapsed = time.time() - start
        logger.error("Model call failed after %.1fs: %s", elapsed, exc)
        raise RuntimeError(f"Model call failed: {exc}") from exc

    elapsed = time.time() - start
    logger.info("Model responded in %.1fs", elapsed)

    # ── Extract text ─────────────────────────────────────────────────
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError(
            "The model returned an empty response. Try a clearer image or a different mode."
        )
    return text


# ---------------------------------------------------------------------------
# CLI helper
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if len(sys.argv) < 2:
        print("Usage: python tutor.py <image_path> [mode] [level]")
        print(f"  modes:  {', '.join(sorted(VALID_MODES))}")
        print(f"  levels: {', '.join(sorted(VALID_LEVELS))}")
        sys.exit(1)

    img_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "explain"
    level = sys.argv[3] if len(sys.argv) > 3 else "intermediate"
    mime_type = mimetypes.guess_type(img_path)[0] or "image/jpeg"

    with open(img_path, "rb") as f:
        result = run_tutor(f.read(), mime_type, mode=mode, level=level)
    print(result)
