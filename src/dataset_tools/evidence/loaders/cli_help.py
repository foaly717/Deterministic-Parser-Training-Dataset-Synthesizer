import hashlib
import re
from pathlib import Path

from dataset_tools.evidence.ids import compute_document_id, compute_fact_id
from dataset_tools.evidence.loaders.base import EvidenceLoader
from dataset_tools.evidence.schema import (
    ArtifactIdentity,
    DocumentFormat,
    DocumentMetadata,
    NormalizedEvidenceDocument,
    NormalizedEvidenceFact,
    Provenance,
    SemanticPredicate,
    ToolIdentity,
)


def extract_cli_option_facts(
    content: str,
    doc_id: str,
    subject: str = "cli",
) -> list[NormalizedEvidenceFact]:
    facts: list[NormalizedEvidenceFact] = []
    lines = content.splitlines()

    option_pattern = re.compile(
        r"^\s*((?:--?[^\s,]+,?\s*)+)"
        r"(<[^>]+>|\S+)?\s*(.*)$"
    )
    usage_option_pattern = re.compile(
        r"(?<!\w)--?[A-Za-z0-9][A-Za-z0-9_-]*"
    )

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if re.match(r"^(usage:|Usage:)", stripped):
            options = usage_option_pattern.findall(stripped)
            description = "Referenced in usage syntax"
            argument = "none"
        elif stripped.startswith("-") and not stripped.startswith("---"):
            match = option_pattern.match(line)
            if not match:
                continue

            raw_options, argument, description = match.groups()
            options = [
                option.strip().rstrip(",")
                for option in raw_options.split(",")
                if option.strip()
            ]
            argument = argument or "none"
            description = description or "No description"
        else:
            continue

        for option in options:
            provenance = Provenance(
                line_start=line_number,
                line_end=line_number,
                raw_snippet=line,
            )

            facts.append(
                NormalizedEvidenceFact(
                    fact_id=compute_fact_id(
                        doc_id,
                        subject,
                        SemanticPredicate.SUPPORTS.value,
                        option,
                        provenance.model_dump(),
                    ),
                    document_id=doc_id,
                    subject=subject,
                    predicate=SemanticPredicate.SUPPORTS,
                    value=option,
                    provenance=provenance,
                )
            )

    return facts


class CLIHelpLoader(EvidenceLoader):
    def supports(self, path: Path) -> bool:
        if path.suffix.lower() not in {".txt", ".help"}:
            return False

        try:
            content = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            return False

        return bool(
            re.search(r"(?im)^usage:\s", content)
            and re.search(
                r"(^|\s)--?[A-Za-z0-9]",
                content,
            )
        )

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

        subject = source_id.removesuffix("-help").removesuffix("_help")

        return NormalizedEvidenceDocument(
            document_id=document_id,
            artifact=ArtifactIdentity(
                source_id=source_id,
                source_sha256=source_sha256,
                path_or_uri=str(path),
            ),
            metadata=DocumentMetadata(
                format=DocumentFormat.CLI_HELP,
                tool=ToolIdentity(name=subject),
            ),
            facts=extract_cli_option_facts(
                content=content,
                doc_id=document_id,
                subject=subject,
            ),
        )
