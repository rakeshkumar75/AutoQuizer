import json
from dataclasses import dataclass
from pathlib import Path

from agent.config import SUPPORTED_INPUT_EXTENSIONS, Settings
from agent.pipeline import VideoQuizPipeline


@dataclass
class FileObservation:
    size: int
    stable_count: int


class FolderWatcher:
    def __init__(
        self,
        settings: Settings,
        pipeline: VideoQuizPipeline,
    ) -> None:
        self.settings = settings
        self.pipeline = pipeline
        self.observations: dict[Path, FileObservation] = {}
        self.manifest_path = settings.state_dir / "processed.json"
        self.processed_records = self._load_manifest()

    def scan(self):
        current_files = set()

        for path in sorted(self.settings.input_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
                continue

            current_files.add(path)
            signature = self._build_signature(path)
            if signature in self.processed_records:
                continue

            if self._is_stable(path):
                self._process_path(path, signature)

        for path in set(self.observations) - current_files:
            self.observations.pop(path, None)



    def _load_manifest(self):
        if not self.manifest_path.exists():
            return {}

        return json.loads(self.manifest_path.read_text(encoding="utf-8"))


    def _save_manifest(self):
        self.manifest_path.write_text(json.dumps(self.processed_records, indent=4))

    def _build_signature(self, path: Path) -> str:
        stat = path.stat()
        return f"{stat.st_size}:{stat.st_mtime_ns}"

    def _is_stable(self, path: Path) -> bool:
        signature = self._build_signature(path)
        observation = self.observations.get(path)
        if observation is None or observation.size != path.stat().st_size:
            self.observations[path] = FileObservation(
                size=path.stat().st_size,
                stable_count=1,
            )
            return False

        observation.stable_count += 1
        return observation.stable_count >= self.settings.stable_polls_required

    def _process_path(self, path: Path, signature: str) -> None:
        self.pipeline.process(path)
        self.processed_records[signature] = {"path": str(path)}
        self._save_manifest()