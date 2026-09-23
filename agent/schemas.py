from typing import List, Optional, TypedDict

from pydantic import BaseModel, Field

class NoteSection(BaseModel):

    heading: str = Field(description="Note heading")
    bullets : list[str] = Field(description = "Note bullets")

class NotesDocument(BaseModel):
    title: str = Field(description="Note title") 
    overview: str = Field(description="Note overview")
    sections: List[NoteSection] = Field(description="Note sections")
    keywords: List[str] = Field(description="Note keywords")

class SummaryDocument(BaseModel):
    headline: str = Field(description="Summary heading")
    short_summary: str = Field(description="Summary summary")
    key_takeaways: List[str] = Field(description="Summary key takeaways")


class QuizQuestions(BaseModel):
    question: str = Field(description="Question")
    options: List[str] = Field(description="Options")
    answer_index: int = Field(description="Index of answer")
    explanation: str = Field(description="Explanation")


class QuizDocument(BaseModel):
    title: str = Field(description="Quiz title")
    questions: List[QuizQuestions] = Field(description="Quiz questions")

class PipelineState(TypedDict, total=False):
    video_path: str
    video_name: str
    transcript: str
    output_dir: str
    notes: Optional[NotesDocument]
    summary: Optional[SummaryDocument]
    quiz: Optional[QuizDocument]






