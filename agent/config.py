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
    api_key: str
    input_dir: Path
    output_dir: Path
    state_dir: Path
    poll_seconds: int
    stable_polls_required: int
    transcription_model: str
    generation_model: str
    quiz_question_count: int
    max_transcription_bytes: int

    @classmethod
    def from_env(cls) -> "Settings":
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(env_path)
        load_dotenv()

        api_key = (
            os.getenv("GOOGLE_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )
        if not api_key:
            raise RuntimeError(
                "A Google Studio API key is required. Add it to your environment or .env file "
                "using GOOGLE_API_KEY, GEMINI_API_KEY, or API_KEY."
            )

        drop_dir_env = os.getenv("VIDEO_DROP_DIR")
        if drop_dir_env:
            input_dir = Path(drop_dir_env).expanduser().resolve()
        elif Path("incoming_videos").exists() and any(Path("incoming_videos").iterdir()):
            input_dir = Path("incoming_videos").expanduser().resolve()
        elif Path("incoming_video").exists() and any(Path("incoming_video").iterdir()):
            input_dir = Path("incoming_video").expanduser().resolve()
        else:
            input_dir = Path("incoming_videos").expanduser().resolve()
        output_dir = Path(os.getenv("OUTPUT_DIR", "output")).expanduser().resolve()
        state_dir = output_dir / "_state"

        return cls(
            api_key=api_key,
            input_dir=input_dir,
            output_dir=output_dir,
            state_dir=state_dir,
            poll_seconds=int(os.getenv("WATCH_POLL_SECONDS", "5")),
            stable_polls_required=int(os.getenv("STABLE_POLLS_REQUIRED", "2")),
            transcription_model=os.getenv("GOOGLE_TRANSCRIBE_MODEL", "gemini-3.6-flash"),
            generation_model=os.getenv("GOOGLE_TEXT_MODEL", "gemini-3.6-flash"),
            quiz_question_count=int(os.getenv("QUIZ_QUESTION_COUNT", "10")),
            max_transcription_bytes=int(
                os.getenv("GOOGLE_MAX_TRANSCRIPTION_BYTES", str(DEFAULT_MAX_TRANSCRIPTION_BYTES))
            ),
        )

    def ensure_directories(self) -> None:
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
