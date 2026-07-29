from pathlib import Path
from pyexpat.errors import messages
from typing import TypeVar

from openai import OpenAI

from agent.schemas import *
from config import Settings


class OpenAIService:

    def _init_(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

    # Transcription

    SchemaModel = TypeVar("SchemaModel", bound=BaseModel)

    def transcribe(self, video_path: Path):
        file_size = video_path.stat().st_size

        if file_size > self.settings.max_transcription_bytes:
            raise ValueError(
                "The maximum transcription size is {} bytes".format(file_size)
            )

        with open(video_path, "rb") as video_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.settings.transcription_model,
                file=video_file,
            )

        text = getattr(transcript, "text", "")

        if text:
            text.strip()

        return text


    def create_notes(self, transcript: str) -> NotesDocument:
        system_prompt = (
            "You are a teaching assistant. Convert raw transcript text into clean study notes "
            "Fix grammar, remove filler words, keep the ideas accurate "
            "Organize the notes clearly "
        )

        user_prompt = (
            "Create a well-structured notes from this transcript"
            f"Transcript : {transcript}"
        )

        return self.parse_response(NotesDocument, system_prompt = system_prompt, user_prompt = user_prompt)

    def create_summary(self, transcript: str, notes: NotesDocument) -> SummaryDocument:
        system_prompt = (
            "you summarize leaning material for busy student",
            "produce a short, crip summary and the most import takeaways"
        )

        user_prompt = (
            "Summarize the following content",
            f"Transcript : {transcript}",
            f"Notes : {notes}"
        )

        return self.parse_response(SummaryDocument, system_prompt=system_prompt, user_prompt=user_prompt)

    def create_quiz(self, transcript: str, notes: NotesDocument) -> QuizDocument:
        system_prompt = (
            "you create short multiple choice quizzes from the study materials"
            f"Write clear questions, {self.settings.number_of_questionns} options for each question, correct option number, explanation"
        )

        user_prompt = (
            "Create a short quiz from the study materials",
            f"Transcript: {transcript}"
            f"Notes : {notes}"
        )

        return self.parse_response(QuizDocument, system_prompt=system_prompt, user_prompt=user_prompt)

    
    def parse_response(self, schema : type[SchemaModel], system_prompt, user_prompt) -> SchemaModel :
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        parse_method = getattr(self.client.responses, "parse_response")

        if callable(parse_method):
            response = parse_method(
                model=self.settings.generation_model,
                inputs=messages,
                text_format=schema
            )

            parsed = getattr(response, "parsed")

            if isinstance(parsed, schema):
                return parsed

            if parsed is not None:
                return schema.model_validate(parsed)