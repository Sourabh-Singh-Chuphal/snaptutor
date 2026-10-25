# SnapTutor: Step-by-Step Build Guide

Goal: a working, demo-ready app by 3:00 PM that targets both **Best Use of Gemma 4** and **Best Open-Source AI Project**.

---

## Phase 0: Before 10:30 (do this now, 20 minutes)

1. **Get an API key.** Open Google AI Studio, create a Gemini API key, and copy it.
2. **Create the GitHub repo.** Name it `snaptutor`, make it public, add the MIT license and a Python `.gitignore`. Clone it.
3. **Set up Python.**
   ```bash
   cd snaptutor
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install flask google-genai python-dotenv gunicorn
   ```
4. **Create `.env`** with `GEMINI_API_KEY=your_key_here` and confirm `.env` is in `.gitignore`.
5. **Smoke test the model** with a 10-line script before anything else (see Phase 1).
6. Pick 3 sample images for testing: a math problem, a circuit or ER diagram, a handwritten note. Save them in `samples/`.

---

## Phase 1: Prove the core works (10:30-11:00)

Goal: one image in, one explanation out, from a script. Nothing else.

```python
from google import genai
from google.genai import types
client = genai.Client()  # reads GEMINI_API_KEY from the environment
img = open("samples/problem1.jpg", "rb").read()
resp = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents=[types.Part.from_bytes(data=img, mime_type="image/jpeg"),
              "Explain this problem step by step."],
)
print(resp.text)
```

Checks:
- Does it read the image correctly? Try all 3 samples.
- Is the latency acceptable (under about 15 seconds)? If not, stay on the 26b-a4b model.
- If you get a model-not-found error, list models and copy the exact ID from the docs.

**Decision point:** if the image path fails after 15 minutes, switch to the `files.upload` approach. If that also fails, ask a mentor at the venue; do not burn the morning on it.

Commit: `chore: smoke test for Gemma 4 image input`.

---

## Phase 2: The skill + core logic (11:00-12:00)

1. Write `skills/snaptutor/SKILL.md` (frontmatter `name` and `description`, then the tutoring rules). The starter file in this folder is a good base; edit the voice to your taste.
2. Write `tutor.py` with one function: `run_tutor(image_bytes, mime, mode, level, subject, question)`.
   - Load the skill file at startup.
   - Build the prompt: skill text, then mode instructions, then the student's context.
   - Modes: `explain`, `hint`, `quiz`.
3. Test each mode from the command line on all 3 samples. Read the outputs critically:
   - Does `hint` avoid giving away the answer?
   - Does `quiz` produce questions that are actually answerable?
   - Does it admit when the image is unreadable?
4. Tune the skill wording until the outputs are consistently good. This tuning is the real "AI work" judges care about.

Commit: `feat: tutoring skill and core logic`.

---

## Phase 3: Web app (12:00-1:30)

1. `app.py` with three routes: `/` (page), `/api/solve` (POST image + options), `/health`.
2. Validate uploads: allow only png, jpg, jpeg, webp; maximum 8 MB; reject anything else with a clear message.
3. Add a timeout and a try/except that returns a friendly error instead of a stack trace.
4. `templates/index.html`: upload (with camera capture on mobile), preview, level selector, three buttons (Explain, Hint, Practice questions), loading state, rendered markdown output.
5. Test on your phone too (same Wi-Fi, `flask run --host 0.0.0.0`). A phone-camera demo is a strong moment.

Commit after each working piece.

---

## Phase 4: Polish and ship (1:30-2:00, then 2:00-3:00 during lunch)

1. README: problem, how it works, architecture, setup, why it fits both prizes (use the template provided).
2. Screenshot the app and add to the README.
3. Record a 60-90 second backup demo video in case Wi-Fi fails.
4. Push to GitHub and verify the repo from a clean clone: `git clone`, create a venv, `pip install -r requirements.txt`, run. If it fails on a clean clone, a judge's run will too.
5. Stretch only if everything above works: deploy on DigitalOcean App Platform (run command: `gunicorn app:app`, env var `GEMINI_API_KEY`).

---

## Phase 5: Demo prep (2:00-3:00)

90-second script (also in `DEMO.md`):
1. **Problem (15s):** "Students get stuck on a problem at night with nobody to ask."
2. **Live demo (45s):** photograph a handwritten or textbook problem, click Explain, scroll the steps, click Practice questions.
3. **Why it is open (20s):** "Powered by Gemma 4, an open-weights model. The tutoring behavior is a reusable Agent Skill in the repo that anyone can drop into their own agent."
4. **Close (10s):** repo link and what you would add next (multi-language, offline with Ollama).

Have the backup video open in another tab. Pre-load one sample image on your laptop and one on your phone.

---

## Time and risk rules

- If a feature is not working by 1:30 PM, cut it.
- Do not add accounts, databases, or fancy styling.
- Commit every 20-30 minutes so you always have a working version.
- Rate limits: if you hit them, wait a minute, retry, or switch to the smaller model.
- Never commit your API key. If you do, rotate it immediately.

## Submission checklist

- [ ] Public repo with MIT license
- [ ] README with setup, screenshots, and prize-fit section
- [ ] `skills/snaptutor/SKILL.md` present and referenced in the README
- [ ] `.env.example` present, no real key anywhere in git history
- [ ] Demo video link and live demo tested
- [ ] Submission form filled with both prize categories selected, if allowed
