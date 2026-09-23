import argparse
import os
from pathlib import Path
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from google import genai
# pyrefly: ignore [missing-import]
from google.genai import errors


def find_latest_transcript(base_dir: Path) -> str | None:
    output_dir = base_dir / "output"
    if not output_dir.exists():
        return None

    transcript_files = sorted(output_dir.rglob("transcript.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not transcript_files:
        return None

    return transcript_files[0].read_text(encoding="utf-8")


def get_api_key() -> str:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)
    load_dotenv()
    api_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is missing. Add it in the .env file before running this script.")
    return api_key


def ask_python(question: str, client: genai.Client | None = None, transcript: str | None = None) -> str:
    if client is None:
        client = genai.Client(api_key=get_api_key())

    if transcript is None:
        project_dir = Path(__file__).resolve().parent
        transcript = find_latest_transcript(project_dir)

    if not transcript:
        return "This is not in the uploaded video (no transcript is available)."

    prompt = (
        "You are a helpful assistant answering questions strictly based on the provided transcript of an uploaded video.\n\n"
        "Strict Guidelines:\n"
        "- If the answer to the question is found in or directly related to the transcript, provide a clear, accurate, and concise answer using only facts from the transcript.\n"
        "- If the question is NOT related to the transcript or the topic is NOT covered in the uploaded video, you MUST reply with:\n"
        "  \"This is not in the uploaded video.\"\n"
        "- Do NOT answer using outside knowledge if it is not in the transcript.\n\n"
        f"Transcript:\n{transcript}\n\n"
        f"Question: {question}"
    )

    model = os.getenv("GOOGLE_TEXT_MODEL", "gemini-3.6-flash")
    for attempt in range(4):
        try:
            chat = client.chats.create(model=model)
            response = chat.send_message(prompt)
            return response.text.strip()
        except (errors.ServerError, errors.APIError) as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                match = re.search(r"retry in (\d+(?:\.\d+)?)s", err_str, re.IGNORECASE)
                wait_time = float(match.group(1)) + 1.0 if match else 15.0
                if attempt < 3:
                    time.sleep(min(wait_time, 20.0))
                    continue
                return "⚠️ API rate limit reached. Please wait a moment before trying again."
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
            else:
                return f"⚠️ API Error: {e}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask questions using AutoQuizer and Google Studio.")
    parser.add_argument("question", nargs="?", help="Single question to ask immediately.")
    args = parser.parse_args()

    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    project_dir = Path(__file__).resolve().parent
    transcript = find_latest_transcript(project_dir)

    if args.question:
        print(ask_python(args.question, client=client, transcript=transcript))
        return

    print("=" * 60)
    print("🎓 AutoQuizer Study Assistant")
    print("=" * 60)
    print("Type 'exit' or 'quit' anytime to leave.\n")

    first_prompt = True
    while True:
        if first_prompt:
            prompt_text = "What do you want to learn today?\n> "
            first_prompt = False
        else:
            prompt_text = "\nWhat else would you like to learn? (or type 'exit' to quit)\n> "

        try:
            question = input(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not question:
            continue
        if question.lower() in {"exit", "quit", "bye"}:
            print("Goodbye!")
            break

        print("\nThinking...\n")
        try:
            answer = ask_python(question, client=client, transcript=transcript)
            print(f"Answer:\n{answer}\n")
        except Exception as e:
            print(f"Error getting answer: {e}\n")


if __name__ == "__main__":
    main()
