# SnapTutor

Snap a photo of a problem, diagram, or handwritten notes. SnapTutor explains it step by step, gives you hints without spoiling the answer, or turns it into practice questions. Powered by **Gemma 4**, an open-weights multimodal model, through the Gemini API.

Built for Hacktoberfest Hack Day Hyderabad.

## Why it exists

Students often get stuck late at night with nobody to ask. Typing a diagram or a handwritten equation into a chatbot is slow. SnapTutor takes a photo and teaches instead of just giving the answer.

## Features

- Photo in, explanation out (text and diagrams)
- Three modes: **Explain**, **Hint only**, **Practice questions**
- Three levels: beginner, intermediate, exam prep
- Mobile-friendly, works with the phone camera
- Tutoring behavior defined in a reusable **Agent Skill** (`skills/snaptutor/SKILL.md`)

## How it works

```
Browser (photo + options)
        |
        v
Flask  /api/solve  --> validates image
        |
        v
tutor.py  --> loads skills/snaptutor/SKILL.md
          --> builds prompt (skill + mode + level)
          --> Gemma 4 via Gemini API (image + prompt)
        |
        v
Markdown answer --> rendered in the browser
```

## Open source and Gemma 4

- **Gemma 4** is an open-weights model with native image understanding. SnapTutor uses that multimodal input as its core feature.
- The tutoring logic lives in a standalone **Agent Skill** following the open SKILL.md standard. Anyone can copy `skills/snaptutor/` into their own agent.
- The project is MIT licensed, has no proprietary dependencies in the app logic, and the model can be swapped by changing one environment variable.

## Run it locally

```bash
git clone https://github.com/Sourabh-Singh-Chuphal/snaptutor.git
cd snaptutor
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then add your GEMINI_API_KEY
python app.py
```

Open http://localhost:5000. Get a free API key from Google AI Studio.

Quick CLI test without the web UI:

```bash
python tutor.py samples/problem1.jpg explain
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | none | API key from Google AI Studio |
| `GEMMA_MODEL` | `gemma-4-26b-a4b-it` | Use `gemma-4-31b-it` for the larger model |
| `PORT` | `5000` | Server port |

## Deploy (DigitalOcean App Platform)

Run command: `gunicorn app:app`. Set `GEMINI_API_KEY` as an encrypted environment variable.

## Roadmap

- Offline mode with Gemma 4 through Ollama
- Multi-language explanations
- Follow-up questions in a chat thread
- More skills (code review from screenshots, lab report checking)

## License

MIT
