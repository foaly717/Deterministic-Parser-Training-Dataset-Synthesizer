import hashlib
from pathlib import Path

from dataset_tools.parsers.man_models import ManEntry


def parse_man_page(
    file_path: Path,
    tool_name: str | None = None,
) -> list[ManEntry]:
    text = file_path.read_text(encoding="utf-8")
    sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()

    entries: list[ManEntry] = []
    current_section: str | None = None
    current_description: list[str] = []
    section_line: int | None = None

    def flush_section() -> None:
        if current_section is None:
            return

        description = " ".join(current_description).strip()

        entries.append(
            ManEntry(
                name=current_section,
                section=current_section,
                description=description or None,
                source_id=file_path.stem,
                source_sha256=sha256,
                line_start=section_line,
                line_end=section_line,
                tool=tool_name,
            )
        )

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()

        if stripped.startswith(".SH"):
            flush_section()
            current_description.clear()
            current_section = stripped.replace(".SH", "", 1).strip()
            section_line = line_number
            continue

        if current_section is not None and stripped:
            current_description.append(stripped.replace("\\\\-", "-"))

    flush_section()

    return entries
