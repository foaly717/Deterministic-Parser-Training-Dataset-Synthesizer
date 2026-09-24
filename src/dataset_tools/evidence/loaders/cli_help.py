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


SECTION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ]*\s+-{4,}")
DECLARATION_RE = re.compile(
    r"^[ \t]*(?:-[A-Za-z0-9][.,]?|--[A-Za-z0-9-]+[.,]?)"
)
FLAG_RE = re.compile(r"--?[A-Za-z0-9][A-Za-z0-9_:-]*")
ARGUMENT_RE = re.compile(r"<[^>\n]+>")


def _parse_declaration(
    line: str,
) -> tuple[list[str], str | None, str]:
    stripped = line.strip()

    argument_match = ARGUMENT_RE.search(stripped)

    if argument_match:
        declaration_end = argument_match.end()
        argument = argument_match.group(0)
        declaration = stripped[:declaration_end]
        inline_description = stripped[declaration_end:].strip()
    else:
        argument = None
        declaration = stripped
        inline_description = ""

        match = re.match(r"^((?:-[^\s,]+,?\s*)+)(.*)$", stripped)
        if match:
            declaration = match.group(1).strip()
            inline_description = match.group(2).strip()

    flags = FLAG_RE.findall(declaration)

    return flags, argument, inline_description


def _extract_enum_values(description: str) -> list[str]:
    values: list[str] = []
    collecting = False

    for line in description.splitlines():
        value = line.strip()

        if value.endswith(":"):
            collecting = True
            continue

        if not collecting:
            continue

        if not value:
            continue

        if (
            " " not in value
            and ":" not in value
            and "=" not in value
            and len(value) < 40
        ):
            values.append(value)
        else:
            collecting = False

    return values


def _extract_implied_options(description: str) -> list[str]:
    return re.findall(
        r"\bimplies\s+(--?[A-Za-z0-9][A-Za-z0-9_:-]*)\b",
        description,
        flags=re.IGNORECASE,
    )


def _build_declaration_facts(
    *,
    document_id: str,
    subject: str,
    flags: list[str],
    argument: str | None,
    description: str,
    section: str | None,
    line_start: int,
    line_end: int,
    raw_lines: list[str],
) -> list[NormalizedEvidenceFact]:
    provenance = Provenance(
        line_start=line_start,
        line_end=line_end,
        section=section,
        raw_snippet="\n".join(raw_lines),
    )

    facts: list[NormalizedEvidenceFact] = []

    for flag in flags:
        facts.append(
            NormalizedEvidenceFact(
                fact_id=compute_fact_id(
                    document_id,
                    subject,
                    SemanticPredicate.SUPPORTS.value,
                    flag,
                    provenance.model_dump(),
                ),
                document_id=document_id,
                subject=subject,
                predicate=SemanticPredicate.SUPPORTS,
                value=flag,
                provenance=provenance,
            )
        )

    primary_flag = next(
        (flag for flag in flags if flag.startswith("--")),
        flags[0] if flags else subject,
    )

    if argument is not None and argument.startswith("<") and argument.endswith(">"):
        expected_type = argument[1:-1]
        facts.append(
            NormalizedEvidenceFact(
                fact_id=compute_fact_id(
                    document_id,
                    primary_flag,
                    SemanticPredicate.ACCEPTS_TYPE.value,
                    expected_type,
                    provenance.model_dump(),
                ),
                document_id=document_id,
                subject=primary_flag,
                predicate=SemanticPredicate.ACCEPTS_TYPE,
                value=expected_type,
                provenance=provenance,
            )
        )

    for enum_value in _extract_enum_values(description):
        facts.append(
            NormalizedEvidenceFact(
                fact_id=compute_fact_id(
                    document_id,
                    primary_flag,
                    SemanticPredicate.ENUMERATES.value,
                    enum_value,
                    provenance.model_dump(),
                ),
                document_id=document_id,
                subject=primary_flag,
                predicate=SemanticPredicate.ENUMERATES,
                value=enum_value,
                provenance=provenance,
            )
        )

    for implied_option in _extract_implied_options(description):
        facts.append(
            NormalizedEvidenceFact(
                fact_id=compute_fact_id(
                    document_id,
                    primary_flag,
                    SemanticPredicate.REQUIRES.value,
                    implied_option,
                    provenance.model_dump(),
                ),
                document_id=document_id,
                subject=primary_flag,
                predicate=SemanticPredicate.REQUIRES,
                value=implied_option,
                provenance=provenance,
            )
        )

    return facts


def extract_cli_option_facts(
    content: str,
    doc_id: str,
    subject: str = "cli",
) -> list[NormalizedEvidenceFact]:
    lines = content.splitlines()
    facts: list[NormalizedEvidenceFact] = []

    current_section: str | None = None
    current_flags: list[str] | None = None
    current_argument: str | None = None
    current_description: list[str] = []
    current_raw_lines: list[str] = []
    current_start: int | None = None
    current_end: int | None = None

    def flush() -> None:
        nonlocal current_flags
        nonlocal current_argument
        nonlocal current_description
        nonlocal current_raw_lines
        nonlocal current_start
        nonlocal current_end

        if not current_flags or current_start is None or current_end is None:
            current_flags = None
            current_argument = None
            current_description = []
            current_raw_lines = []
            current_start = None
            current_end = None
            return

        facts.extend(
            _build_declaration_facts(
                document_id=doc_id,
                subject=subject,
                flags=current_flags,
                argument=current_argument,
                description="\n".join(current_description),
                section=current_section,
                line_start=current_start,
                line_end=current_end,
                raw_lines=current_raw_lines,
            )
        )

        current_flags = None
        current_argument = None
        current_description = []
        current_raw_lines = []
        current_start = None
        current_end = None

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if SECTION_RE.match(stripped):
            flush()
            current_section = stripped.split("----", 1)[0].strip()
            continue

        if re.match(r"^(usage:|Usage:)", stripped):
            flush()

            options = re.findall(
                r"(?<!\w)--?[A-Za-z0-9][A-Za-z0-9_:-]*",
                stripped,
            )

            if options:
                provenance = Provenance(
                    line_start=line_number,
                    line_end=line_number,
                    raw_snippet=line,
                )

                for option in options:
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
            continue

        if DECLARATION_RE.match(line):
            flush()

            flags, argument, inline_description = _parse_declaration(line)

            current_flags = flags
            current_argument = argument
            current_description = (
                [inline_description] if inline_description else []
            )
            current_raw_lines = [line]
            current_start = line_number
            current_end = line_number
            continue

        if current_flags is not None:
            current_raw_lines.append(line)
            current_end = line_number

            if stripped:
                current_description.append(stripped)

    flush()

    return facts


class CLIHelpLoader(EvidenceLoader):
    def __init__(
        self,
        tool_name: str | None = None,
        filename: str | None = None,
    ):
        self.tool_name = tool_name
        self.filename = filename

    def supports(self, path: Path) -> bool:
        if self.filename is not None and path.name != self.filename:
            return False

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

        subject = self.tool_name or (
            source_id.removesuffix("-help").removesuffix("_help")
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
                tool=ToolIdentity(name=subject),
            ),
            facts=extract_cli_option_facts(
                content=content,
                doc_id=document_id,
                subject=subject,
            ),
        )
