import datetime
import json
from pathlib import Path
import re

from langgraph.graph import StateGraph, START, END

from agent.config import Settings
from agent.openai_service import OpenAIStudyHelper
from agent.schemas import NotesDocument, PipelineState, QuizDocument, SummaryDocument


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return cleaned or "video"


def build_output_dir(video_path: Path, base_output_dir: Path) -> Path:
    modified_time = datetime.fromtimestamp(
        video_path.stat().st_mtime
    ).strftime("%Y%m%d-%H%M%S")
    return base_output_dir / f"{_slugify(video_path.stem)}-{modified_time}"


def render_notes_markdown(notes: NotesDocument) -> str:
    lines = [f"# {notes.title}", "", "## Overview", notes.overview, ""]

    for section in notes.sections:
        lines.append(f"### {section.heading}")
        if section.bullets:
            lines.extend(f"- {bullet}" for bullet in section.bullets)
        else:
            lines.append("- No bullets generated.")
        lines.append("")

    if notes.keywords:
        lines.append("## Keywords")
        lines.extend(f"- {keyword}" for keyword in notes.keywords)
        lines.append("")

    return "\n".join(lines).strip() + "\n"

def render_summary_markdown(summary: SummaryDocument) -> str:
    lines = [
        f"# {summary.headline}",
        "",
        "## Short Summary",
        summary.short_summary,
        "",
        "## Key Takeaways",
    ]

    lines.extend(f"- {takeaway}" for takeaway in summary.key_takeaways)
    lines.append("")
    return "\n".join(lines)


def render_quiz_markdown(quiz: QuizDocument) -> str:
    lines = [f"# {quiz.title}", ""]

    for index, question in enumerate(quiz.questions, start=1):
        lines.append(f"## Question {index}")
        lines.append(question.question)
        lines.append("")

        for option_index, option in enumerate(question.options, start=1):
            lines.append(f"{option_index}. {option}")

        lines.append("")
        lines.append(f"Answer: Option {question.answer_index + 1}")
        lines.append(f"Explanation: {question.explanation}")
        lines.append("")

    return "\n".join(lines)

class VideoQuizPipeline:
    def _init_(self, settings: Settings) -> None:
        self.settings = settings
        self.ai = OpenAIStudyHelper(settings)
        self.graph = self._build_graph()

    def process(self, video_path: Path) -> dict[str, object]:
        output_dir = build_output_dir(video_path, self.settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        state = self.graph.invoke(
            {
                "video_path": str(video_path),
                "video_name": video_path.name,
                "output_dir": str(output_dir),
            }
        )

        return dict(state)


    def _build_graph(self):
        builder = StateGraph(PipelineState)
        builder.add_node("transcribe", self._transcribe_node)
        builder.add_node("notes", self._notes_node)
        builder.add_node("quiz", self._quiz_node)
        builder.add_node("summary", self._summary_node)
        builder.add_node("persist", self._persist_node)

        builder.add_edge(START, "transcribe")
        builder.add_edge("transcribe", "notes")
        builder.add_edge("notes", "summary")
        builder.add_edge("summary", "quiz")
        builder.add_edge("quiz", "persist")
        builder.add_edge("persist", END)
        return builder.compile()

    def _transcribe_node(self, state: PipelineState):
        video_path = Path(state["video_path"])
        transcript = self.ai.transcribe(video_path)
        return {
            "transcript": transcript,
        }

    def _notes_node(self, state: PipelineState):
        notes = self.ai.create_notes(state["transcript"])
        return {"notes": notes}

    def _summary_node(self, state: PipelineState):
        summary = self.ai.create_summary(state["transcript"], state["notes"])
        return {"summary": summary}


    def _quiz_node(self, state: PipelineState):
        quiz = self.ai.create_quiz(state["transcript"], state["notes"])
        return {"quiz": quiz} 

    def _persist_node(self, state: PipelineState) -> PipelineState:
        output_dir = Path(state["output_dir"])
        notes = state["notes"]
        summary = state["summary"]
        quiz = state["quiz"]

        transcript_path = output_dir / "transcript.txt"
        notes_path = output_dir / "notes.md"
        summary_path = output_dir / "summary.md"
        quiz_markdown_path = output_dir / "quiz.md"
        result_path = output_dir / "result.json"

        transcript_path.write_text(state["transcript"], encoding="utf-8")
        notes_path.write_text(render_notes_markdown(notes), encoding="utf-8")
        summary_path.write_text(render_summary_markdown(summary), encoding="utf-8")
        quiz_markdown_path.write_text(render_quiz_markdown(quiz), encoding="utf-8")

        result_payload = {
            "video_name": state["video_name"],
            "video_path": state["video_path"],
            "transcript": state["transcript"],
            "notes": notes.model_dump(),
            "summary": summary.model_dump(),
            "quiz": quiz.model_dump(),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

        result_path.write_text(json.dumps(result_payload, indent=2), encoding="utf-8",)

        return state
       
    