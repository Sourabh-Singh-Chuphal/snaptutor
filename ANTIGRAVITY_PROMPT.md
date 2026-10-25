# Prompt for Antigravity (paste everything below this line)

---

You are my senior pair-programmer for a one-day hackathon. Read this whole brief, then **ask me clarifying questions before writing any code**.

## 1. Context

- Event: Hacktoberfest Hack Day Hyderabad (MLH). Hacking starts 10:30 AM IST. Demos run 3:00-5:00 PM IST. I have about 4 hours of real build time (lunch 2:00-3:00 PM overlaps).
- I am an early-career software/ML engineer. I am strongest in Python (Flask/Django), Java/Spring Boot, SQL, and ML/NLP. I am comfortable with Git and the terminal.
- I am targeting two prize categories at once:
  1. **Best Use of Gemma 4**: a focused AI tool that uses Gemma 4's multimodal (text + image) ability through the Gemini API, ideally for learning, creativity, productivity, or community.
  2. **Best Open-Source AI Project (DigitalOcean)**: an original project where open-weight AI is an important part of how it works. An agent skill, a build on an open-weight model, or an adapted open-source model harness all count.

## 2. The project: SnapTutor

A web app where a student uploads a photo of something they are stuck on: a textbook problem, a circuit or ER diagram, a graph, a code snippet, or handwritten notes. Gemma 4 reads the image and:

1. Identifies what the image contains (subject, topic, what is being asked).
2. Explains the solution step by step at the student's chosen level (beginner, intermediate, exam-prep).
3. Offers a "hint only" mode that nudges without giving the answer.
4. Generates 3 practice questions (easy, medium, hard) on the same concept, with answers hidden behind a "reveal" toggle.

The tutoring behavior is defined in a reusable **Agent Skill** (`skills/snaptutor/SKILL.md`, following the Agent Skills open standard) so other developers and agents can reuse it. The Flask app loads that skill file at runtime, so the skill is a real part of how the product works and not decoration.

## 3. Technical decisions already made

- Backend: Python 3.11+, Flask, `google-genai` SDK, `python-dotenv`, gunicorn.
- Model: `gemma-4-26b-a4b-it` by default (fast), configurable to `gemma-4-31b-it` through the `GEMMA_MODEL` env var. These IDs are the ones documented for Gemma 4 on the Gemini API. Verify them against the current docs at ai.google.dev/gemma/docs/core/gemma_on_gemini_api before relying on them.
- Image input: send bytes inline with `types.Part.from_bytes(...)`; fall back to `client.files.upload(...)` if inline fails.
- Gemma may not support a separate system instruction on the Gemini API. Put the skill text at the top of the user content instead, and test this early.
- Frontend: one HTML page, vanilla JS, mobile-friendly, renders markdown with `marked` and sanitizes with `DOMPurify` from a CDN. No build step.
- Repo: public, MIT license, `.env.example`, no secrets committed.
- Deploy target (stretch): DigitalOcean App Platform with `gunicorn app:app`.

## 4. Non-goals (do not build these)

- No user accounts, no database, no payments.
- No fine-tuning or training.
- No heavy frontend frameworks.

## 5. Deliverables

1. Working app running locally with `python app.py`.
2. `skills/snaptutor/SKILL.md` that is well-written and standalone.
3. `README.md` with problem statement, architecture diagram (ASCII or Mermaid), setup steps, screenshots placeholder, and an "Open-source and Gemma 4" section explaining why this fits both prize categories.
4. A short `DEMO.md` with a 90-second demo script.
5. Clean commit history (small, meaningful commits).

## 6. How I want you to work

- **First, ask me your questions.** Ask up to 10 in a single batch, numbered, and give a suggested default for each so I can reply "defaults" if I am short on time. Cover anything you think is unclear or risky: input types, level options, language support, error handling, UI preferences, privacy, rate limits, deployment, and what I want to show in the demo.
- After I answer (or say "defaults"), write a short plan with milestones and time estimates, then wait for my "go".
- Build in small milestones. After each milestone, run the code, tell me exactly what you tested and what you could not test, and show me the commands to verify it myself.
- Prefer the simplest thing that works. Flag anything that could burn more than 20 minutes and offer a cheaper alternative.
- Never invent API behavior. If you are unsure about a Gemma 4 or Gemini API detail, say so and check the docs or test it with a tiny script first.
- Keep secrets in `.env`, never in code or commits.
- Add basic safety: file type and size validation, friendly error messages, and a timeout on the model call.
- Tell me when I should stop adding features and start polishing for the 3:00 PM demo.

Start now by asking your questions.
