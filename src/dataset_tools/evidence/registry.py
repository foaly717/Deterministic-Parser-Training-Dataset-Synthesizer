from pathlib import Path

from .loaders.base import EvidenceLoader
from .loaders.handbrakecli import HandBrakeCliLoader
from .loaders.markdown import MarkdownEvidenceLoader
from .loaders.text import TextEvidenceLoader


LOADERS: list[EvidenceLoader] = [
    HandBrakeCliLoader(),
    MarkdownEvidenceLoader(),
    TextEvidenceLoader(),
]


def load_evidence(path: Path):
    for loader in LOADERS:
        if loader.supports(path):
            return loader.load(path)

    raise ValueError(
        f"No evidence loader available for {path}"
    )
