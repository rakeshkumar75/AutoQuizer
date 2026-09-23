
# 🎓 AutoQuizer — AI-Powered Video Study Assistant

> **AutoQuizer** is an autonomous study assistant that transforms raw lecture videos and audio files into comprehensive, structured study materials—including organized notes, concise summaries, 10-question multiple-choice quizzes, and an interactive grounded Q&A chatbot.

---

## 📌 Problem It Solves

Students and educators spend hundreds of hours re-watching lecture recordings, taking incomplete manual notes, and struggling to self-assess understanding. 

**AutoQuizer automates this entire learning cycle:**
1. Just drop a video/audio file into an incoming directory.
2. The autonomous pipeline detects, transcribes, summarizes, generates study notes, and compiles self-test quizzes.
3. Chat with an integrated assistant that answers questions **strictly based on the lecture transcript**, eliminating AI hallucinations.

---

## 🚀 Key Features

* 🎙️ **Multimodal Audio/Video Transcription:** Uses Google Gemini’s native multimodal capabilities to transcribe `.mp4`, `.mp3`, `.wav`, `.m4a`, and `.webm` files directly.
* 📝 **Structured Study Notes:** Organizes lectures into titles, overviews, structured sections with bullet points, and core keywords.
* 📊 **Executive Summary:** Generates clear headlines, concise high-level summaries, and critical takeaways for quick revision.
* ❓ **Automated MCQ Generation:** Compiles 10 multiple-choice questions with 4 options, verified answer keys, and pedagogical explanations.
* 🛡️ **Zero-Hallucination Q&A Chatbot:** An interactive CLI assistant (`ask_python.py`) grounded exclusively in the video transcript—refuses to answer out-of-scope questions.
* 🔄 **Stateful LangGraph Pipeline:** Orchestrated as a directed acyclic graph (DAG) with managed state, retry mechanisms, and rate-limit backoff.
* 👁️ **Autonomous Folder Watcher:** Background polling system with duplicate tracking (`processed.json`) and file write-stability verification.
* 📦 **Dual Output Formats:** Generates human-readable Markdown (`.md`) alongside machine-readable JSON (`result.json`).

---

## 🏗️ System Architecture

                            [ User Drops Media File ]
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │   FolderWatcher Engine  │
                             │  (Polls & Checks State) │
                             └────────────┬────────────┘
                                          │
                ┌─────────────────────────┴─────────────────────────┐
                │            LangGraph StateGraph Pipeline          │
                │                                                   │
                │   START                                           │
                │     │                                             │
                │     ▼                                             │
                │ ┌────────────────┐                                │
                │ │  1. Transcribe │ ──▶ Gemini Multimodal Upload   │
                │ └───────┬────────┘                                │
                │         ▼                                         │
                │ ┌────────────────┐                                │
                │ │  2. Make Notes │ ──▶ Gemini + Pydantic Schema   │
                │ └───────┬────────┘                                │
                │         ▼                                         │
                │ ┌────────────────┐                                │
                │ │  3. Summarize  │ ──▶ Headline + Key Takeaways   │
                │ └───────┬────────┘                                │
                │         ▼                                         │
                │ ┌────────────────┐                                │
                │ │  4. Make Quiz  │ ──▶ 10 MCQs + Explanations     │
                │ └───────┬────────┘                                │
                │         ▼                                         │
                │ ┌────────────────┐                                │
                │ │  5. Persist    │ ──▶ Write .md & result.json    │
                │ └───────┬────────┘                                │
                │         ▼                                         │
                │        END                                        │
                └───────────────────────────────────────────────────┘


---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **LLM & Multimodal AI:** (`gemini-3.6-flash`) 
* **Pipeline Orchestration:** 
* **Data Validation & Schemas:** 
* **Environment Configuration:** 

---

## 📂 Project Structure

AutoQuizer/
├── agent/
│   ├── config.py           # Central configuration, env parsing & path resolution
│   ├── schemas.py          # Pydantic data contracts (Notes, Summary, Quiz, State)
│   ├── openai_service.py   # Gemini API client wrapper, retry logic & schema binding
│   ├── pipeline.py         # LangGraph StateGraph pipeline nodes and edges
│   └── trigger.py          # Folder watcher, file stability check & manifest manager
├── incoming_videos/        # Drop directory for target video/audio files
├── output/                 # Generated study artifacts
│   ├── _state/             # Manifest state (processed.json) to prevent duplicate runs
│   └── <lecture-slug-timestamp>/
│       ├── transcript.txt  # Raw verbatim transcription
│       ├── notes.md        # Comprehensive study notes with headers and bullets
│       ├── summary.md      # Executive summary & core takeaways
│       ├── quiz.md         # 10 MCQs with answer keys & explanations
│       └── result.json     # Consolidated machine-readable JSON payload
├── ask_python.py           # Grounded interactive Q&A study chatbot
├── ask.bat / ask.ps1       # Windows terminal launch shortcuts for the chatbot
├── main.py                 # Pipeline entrypoint (continuous watcher or one-off scan)
└── .env.example            # Example configuration template


# Introduction to Python Programming Language

## Question 1
Who created Python and in what year was it invented?

1. Guido van Rossum in 1991
2. James Gosling in 1995
3. Bjarne Stroustrup in 1983
4. Dennis Ritchie in 1972

Answer: Option 1
Explanation: Python was invented in 1991 by Guido van Rossum with an emphasis on code readability.
