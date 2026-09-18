import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeSettings:
    model: str
    endpoint: str
    help_file: Path
    output: Path


def get_settings() -> RuntimeSettings:
    return RuntimeSettings(
        model=os.getenv("MODEL_NAME", "default"),
        endpoint=os.getenv(
            "MODEL_ENDPOINT",
            "http://127.0.0.1:8080/v1/chat/completions",
        ),
        help_file=Path(
            os.getenv(
                "HELP_FILE",
                "data/evidence/handbrakecli-help.txt",
            )
        ),
        output=Path(
            os.getenv(
                "OUTPUT_FILE",
                "data/raw/livefire_20.jsonl",
            )
        ),
    )
