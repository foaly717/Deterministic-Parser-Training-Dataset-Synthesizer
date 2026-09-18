import re

from dataset_tools.evidence.ids import fact_id
from dataset_tools.evidence.schema import (
    FactCategory,
    NormalizedEvidenceFact,
    Provenance,
)


def extract_cli_option_facts(
    content: str,
    doc_id: str,
    source_id: str,
    source_sha256: str,
    subject: str = "cli",
) -> list[NormalizedEvidenceFact]:
    """Extract option facts from standard CLI help text without file loading or side effects."""
    facts: list[NormalizedEvidenceFact] = []
    lines = content.splitlines()

    option_pattern = re.compile(r"^\s*(-\S+)\s+(<[^>]+>|\S+)?\s*(.*)$")
    usage_option_pattern = re.compile(r"(?<![A-Za-z0-9_-])--?[A-Za-z0-9][A-Za-z0-9_-]*")

    for idx, line in enumerate(lines, start=1):
        line_str = line.strip()

        if re.match(r"^(usage:|Usage:)", line_str):
            for match in usage_option_pattern.finditer(line_str):
                opt_name = match.group(0)

                provenance = Provenance(
                    source_id=source_id,
                    source_sha256=source_sha256,
                    line_start=idx,
                    line_end=idx,
                    raw_snippet=line,
                )
                fact = NormalizedEvidenceFact(
                    fact_id=fact_id(
                        doc_id,
                        FactCategory.CLI_OPTION.value,
                        subject,
                        "supports",
                        opt_name,
                        provenance.model_dump(),
                    ),
                    document_id=doc_id,
                    category=FactCategory.CLI_OPTION,
                    subject=subject,
                    predicate="supports",
                    value=opt_name,
                    provenance=provenance,
                    metadata={
                        "kind": "option",
                        "aliases": [],
                        "argument": "none",
                        "description": "Referenced in usage syntax",
                    },
                )
                facts.append(fact)

        elif line_str.startswith("-") and not line_str.startswith("---"):
            match = option_pattern.match(line)
            if match:
                opt_name = match.group(1).strip()
                arg_type = match.group(2) or "none"
                desc = match.group(3) or "No description"

                provenance = Provenance(
                    source_id=source_id,
                    source_sha256=source_sha256,
                    line_start=idx,
                    line_end=idx,
                    raw_snippet=line,
                )
                fact = NormalizedEvidenceFact(
                    fact_id=fact_id(
                        doc_id,
                        FactCategory.CLI_OPTION.value,
                        subject,
                        "supports",
                        opt_name,
                        provenance.model_dump(),
                    ),
                    document_id=doc_id,
                    category=FactCategory.CLI_OPTION,
                    subject=subject,
                    predicate="supports",
                    value=opt_name,
                    provenance=provenance,
                    metadata={
                        "kind": "option",
                        "aliases": [],
                        "argument": arg_type.strip(),
                        "description": desc.strip(),
                    },
                )
                facts.append(fact)

    return facts
