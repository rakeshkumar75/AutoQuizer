import json
import mimetypes
from pathlib import Path
import re
import time
from typing import TypeVar

# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import errors

from pydantic import BaseModel

from agent.config import Settings
from agent.schemas import NotesDocument, QuizDocument, SummaryDocument

SchemaModel = TypeVar("SchemaModel", bound=BaseModel)


class GoogleStudioStudyHelper:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = genai.Client(api_key=settings.api_key)

    # Transcription

    def transcribe(self, video_path: Path):
        file_size = video_path.stat().st_size

        if file_size > self.settings.max_transcription_bytes:
            raise ValueError(
                "The maximum transcription size is {} bytes".format(
                    self.settings.max_transcription_bytes
                )
            )

        mime_type, _ = mimetypes.guess_type(str(video_path))
        upload_kwargs = {"file": video_path}
        if mime_type:
            upload_kwargs["config"] = {"mime_type": mime_type}

        uploaded_file = self.client.files.upload(**upload_kwargs)

        # Poll until the file is active (required for audio/video processing)
        while getattr(uploaded_file, "state", None) and uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = self.client.files.get(name=uploaded_file.name)

        if getattr(uploaded_file, "state", None) and uploaded_file.state.name == "FAILED":
            raise RuntimeError(f"File processing failed: {getattr(uploaded_file, 'error', 'Unknown error')}")

        prompt = (
            "Transcribe this video accurately. Return only the spoken transcript text, "
            "without extra commentary or markdown."
        )

        response = self._generate_with_retry(
            model=self.settings.transcription_model,
            contents=[uploaded_file, prompt],
        )

        text = getattr(response, "text", "")
        return text.strip()

    def create_notes(self, transcript: str) -> NotesDocument:
        system_prompt = (
            "You are a teaching assistant. Convert raw transcript text into clean study notes. "
            "Fix grammar, remove filler words, keep the ideas accurate, and organize the notes clearly."
        )

        user_prompt = (
            "Create a well-structured set of notes from this transcript.\n"
            f"Transcript: {transcript}"
        )

        return self.parse_response(NotesDocument, system_prompt=system_prompt, user_prompt=user_prompt)

    def create_summary(self, transcript: str, notes: NotesDocument) -> SummaryDocument:
        system_prompt = (
            "You summarize learning material for a busy student. "
            "Produce a short, clear summary and the most important takeaways."
        )

        user_prompt = (
            "Summarize the following content.\n"
            f"Transcript: {transcript}\n"
            f"Notes: {notes}"
        )

        return self.parse_response(SummaryDocument, system_prompt=system_prompt, user_prompt=user_prompt)

    def create_quiz(self, transcript: str, notes: NotesDocument) -> QuizDocument:
        system_prompt = (
            "You create short multiple choice quizzes from study materials. "
            f"Write {self.settings.quiz_question_count} clear questions, four options per question, "
            "the correct option number, and an explanation."
        )

        user_prompt = (
            "Create a short quiz from the study materials.\n"
            f"Transcript: {transcript}\n"
            f"Notes: {notes}"
        )

        return self.parse_response(QuizDocument, system_prompt=system_prompt, user_prompt=user_prompt)

    def _generate_with_retry(self, model: str, contents, config=None, max_retries: int = 4):
        last_exception = None
        for attempt in range(max_retries):
            try:
                kwargs = {"model": model, "contents": contents}
                if config:
                    kwargs["config"] = config
                return self.client.models.generate_content(**kwargs)
            except (errors.ServerError, errors.APIError) as e:
                last_exception = e
                err_str = str(e)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str) and attempt < max_retries - 1:
                    match = re.search(r"retry in (\d+(?:\.\d+)?)s", err_str, re.IGNORECASE)
                    wait_time = float(match.group(1)) + 1.0 if match else 15.0
                    time.sleep(min(wait_time, 20.0))
                    continue
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                else:
                    raise
            except Exception as e:
                last_exception = e
                raise
        if last_exception:
            raise last_exception

    def parse_response(self, schema: type[SchemaModel], system_prompt, user_prompt) -> SchemaModel:
        prompt = f"{system_prompt}\n\n{user_prompt}"

        response = self._generate_with_retry(
            model=self.settings.generation_model,
            contents=prompt,
            config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
                "response_schema": schema,
            },
        )

        parsed = getattr(response, "parsed", None)
        if parsed is not None:
            if isinstance(parsed, schema):
                return parsed
            return schema.model_validate(parsed)

        text = getattr(response, "text", "")
        if text:
            try:
                parsed_data = json.loads(text)
                return schema.model_validate(parsed_data)
            except (TypeError, ValueError):
                raise RuntimeError("The model returned a response that could not be parsed into the expected schema.")

        raise RuntimeError("The model returned no structured response.")


OpenAIStudyHelper = GoogleStudioStudyHelper