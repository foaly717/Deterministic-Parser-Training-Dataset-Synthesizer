import hashlib
from pathlib import Path

from dataset_tools.evidence.ids import compute_document_id
from dataset_tools.evidence.loaders.base import EvidenceLoader
from dataset_tools.evidence.loaders.cli_help import extract_cli_option_facts
from dataset_tools.evidence.schema import (
    ArtifactIdentity,
    DocumentFormat,
    DocumentMetadata,
    NormalizedEvidenceDocument,
    ToolIdentity,
)


class FFmpegLoader(EvidenceLoader):
    def supports(self, path: Path) -> bool:
        return "ffmpeg" in path.name.lower()

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(
            encoding="utf-8",
            errors="replace",
        )
        source_id = path.stem
        source_sha256 = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()
        document_id = compute_document_id(
            source_id,
            source_sha256,
        )

        return NormalizedEvidenceDocument(
            document_id=document_id,
            artifact=ArtifactIdentity(
                source_id=source_id,
                source_sha256=source_sha256,
                path_or_uri=str(path),
            ),
            metadata=DocumentMetadata(
                format=DocumentFormat.CLI_HELP,
                tool=ToolIdentity(name="ffmpeg"),
            ),
            facts=extract_cli_option_facts(
                content=content,
                doc_id=document_id,
                subject="ffmpeg",
            ),
        )
