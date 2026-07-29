from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_MAX_TRANSCRIPTION_BYTES = 25 * 1024 * 1024

SUPPORTED_INPUT_EXTENSIONS = (
    ".mp3",
    ".mp4",
    ".mpeg",
    ".mpga",
    ".m4a",
    ".wav",
    ".webm",
)


@dataclass(slots=True)
class Settings:
    openai_api_key: str
    input_dir: Path
    output_dir: Path
    state_dir: Path
    poll_seconds: int
    stable_polls_required: int
    transcription_model: str
    generation_model: str
    quiz_question_count: int
    max_transcription_bytes:int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required. Add it to your environment or .env file.")

        input_dir = Path(os.getenv("VIDEO_DROP_DIR", "incoming_videos")).expanduser().resolve()
        output_dir = Path(os.getenv("OUTPUT_DIR", "output")).expanduser().resolve()
        state_dir = output_dir / "_state"

        return cls(
            openai_api_key=api_key,
            input_dir=input_dir,
            output_dir=output_dir,
            state_dir=state_dir,
            poll_seconds=int(os.getenv("WATCH_POLL_SECONDS", "5")),
            stable_polls_required=int(os.getenv("STABLE_POLLS_REQUIRED", "2")),
            transcription_model=os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe"),
            generation_model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4o"),
            quiz_question_count=int(os.getenv("QUIZ_QUESTION_COUNT", "10")),
            max_transcription_bytes=int(os.getenv("OPENAI_MAX_TRANSCRIPTION_BYTES", str(DEFAULT_MAX_TRANSCRIPTION_BYTES))
            ),
        )

    def ensure_directories(self) -> None:
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)