from pathlib import Path

from dataset_tools.evidence.loaders.handbrakecli import HandBrakeCliLoader
from dataset_tools.evidence.loaders.ffmpeg import FFmpegLoader
from dataset_tools.evidence.loaders.manpage import ManPageLoader
from dataset_tools.evidence.loaders.markdown import MarkdownEvidenceLoader
from dataset_tools.evidence.loaders.text import TextEvidenceLoader
from dataset_tools.evidence.extract_constraints import extract_constraints


LOADERS = [
    HandBrakeCliLoader(),
    FFmpegLoader(),
    MarkdownEvidenceLoader(),
    TextEvidenceLoader(),
    ManPageLoader(),
]


def normalize_document(document):
    document.constraints = extract_constraints(document)
    return document


def load_evidence(path: Path):
    for loader in LOADERS:
        if loader.supports(path):
            return normalize_document(loader.load(path))

    raise ValueError(f"No evidence loader available for: {path}")
