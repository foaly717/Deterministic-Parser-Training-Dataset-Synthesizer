import hashlib
from pathlib import Path

from dataset_tools.evidence.ids import document_id
from dataset_tools.evidence.loaders.base import EvidenceLoader
from dataset_tools.evidence.loaders.cli_help import extract_cli_option_facts
from dataset_tools.evidence.schema import NormalizedEvidenceDocument


class FFmpegLoader(EvidenceLoader):

    def supports(self, path: Path) -> bool:
        return "ffmpeg" in path.name.lower()

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8", errors="replace")
        sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

        source_id = path.stem
        doc_id = document_id(source_id, sha256)

        facts = extract_cli_option_facts(
            content=content,
            doc_id=doc_id,
            source_id=source_id,
            source_sha256=sha256,
            subject="ffmpeg",
        )

        return NormalizedEvidenceDocument(
            document_id=doc_id,
            source_id=source_id,
            source_type="ffmpeg",
            source_sha256=sha256,
            facts=facts,
        )
