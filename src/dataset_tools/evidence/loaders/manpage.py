import hashlib
from pathlib import Path

from dataset_tools.evidence.ids import compute_document_id
from dataset_tools.evidence.loaders.base import EvidenceLoader
from dataset_tools.evidence.schema import (
    ArtifactIdentity,
    DocumentFormat,
    DocumentMetadata,
    NormalizedEvidenceDocument,
    ToolIdentity,
)


class ManPageLoader(EvidenceLoader):
    def supports(self, path: Path) -> bool:
        if ".man." in path.name or path.suffix == ".1":
            return True

        if path.suffix.lower() != ".txt":
            return False

        try:
            content = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            return False

        return bool(
            content.lstrip().startswith(".TH ")
            and "\n.SH " in content
        )

    def load(self, path: Path) -> NormalizedEvidenceDocument:
        content = path.read_text(encoding="utf-8")
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
                format=DocumentFormat.MAN_PAGE,
                tool=ToolIdentity(name=path.stem),
                role="MANUAL",
            ),
            facts=[],
        )
