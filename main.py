import argparse
import time

from agent.config import Settings
from agent.pipeline import VideoQuizPipeline
from agent.trigger import FolderWatcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate notes, summaries, and quizzes from videos.")
    parser.add_argument("--once", action="store_true", help="Scan the input directory once and exit.")
    args = parser.parse_args()

    settings = Settings.from_env()
    settings.ensure_directories()
    watcher = FolderWatcher(settings, VideoQuizPipeline(settings))

    if args.once:
        watcher.scan()
        time.sleep(settings.poll_seconds)
        watcher.scan()
        return

    while True:
        watcher.scan()
        time.sleep(settings.poll_seconds)


if __name__ == "__main__":
    main()