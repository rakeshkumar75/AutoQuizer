import json
from pathlib import Path

from agent.config import Settings
from agent.pipeline import VideoQuizPipeline


class FileObservation:
    size: int
    stable_count: int


class FolderWatcher:
    def _init_(
        self,
        settings: Settings,
        pipeline: VideoQuizPipeline,
    ) -> None:
        self.settings = settings
        self.pipeline = pipeline
        self.observations: dict[Path, FileObservation]
        self.manifest_path = settings.state_dir / "processed.json"
        self.processed_records = self._load_manifest()

    def scan(self):
        current_files = set()

        for path in sorted(self.settings.input_dir.iterdir()):
            if not path.is_file():
                continue

            current_files.add(path)
            signature = self._build_signature()
            if signature in self.processed_records:
                continue

            if self._is_stable(path):
                self._process_path(path, signature)

        stable_path = set(self.observations)
        for i in stable_path :
            self.observations.pop(stable_path, None)



    def _load_manifest(self):
        if not self.manifest_path.exists():
            return {}

        return json.loads(self.manifest_path.read_text(encoding="utf-8"))


    def _save_manifest(self):
        self.manifest_path.write_text(json.dumps(self.processed_records, indent=4))    