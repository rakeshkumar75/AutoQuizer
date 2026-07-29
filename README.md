
## Project structure

- `AutoQuizer/`
  - `agent/`
    - `config.py` — settings and environment config
    - `openai_service.py` — OpenAI transcription + text generation helper
    - `pipeline.py` — media-to-notes/summary/quiz workflow
    - `schemas.py` — Pydantic models for notes, summary, quiz, pipeline state
    - `trigger.py` — folder watcher scaffold for automated processing
  - `video/`
    - `req.txt` — dependencies for AutoQuizer


## AutoQuizer

### What it does

AutoQuizer is designed for students and educators. It converts audio/video lessons into:

- a text transcript
- structured study notes
- a Short summary
- a quiz with questions, options, answers, and explanations

### Core workflow

1. Transcribe media using OpenAI audio transcription
2. Generate clean notes from the transcript
3. Summarize key ideas and takeaways
4. Produce quiz questions from the learning material
5. Save outputs as Markdown and JSON

### Setup

1. Install dependencies:
   ```bash
   pip install -r AutoQuizer/video/req.txt
