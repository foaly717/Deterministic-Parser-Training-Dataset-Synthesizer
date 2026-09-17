import hashlib
import re
from pathlib import Path

from dataset_tools.parsers.cli_models import CLIOption


# A declaration must begin with a CLI flag after optional indentation.
DECLARATION_LINE_RE = re.compile(
    r"^[ \t]*(?:-[A-Za-z0-9][.,]?|--[A-Za-z0-9-]+[.,]?)"
)

# Recognize individual CLI flags.
FLAG_RE = re.compile(r"--?[A-Za-z0-9][A-Za-z0-9-]*")

# Recognize argument specifications such as <string>, <number>, <float>,
# <filename>, or <string:number>.
ARGUMENT_RE = re.compile(r"<[^>\n]+>")

# Section headings in the observed HandBrakeCLI help format.
SECTION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ]*\s+-{4,}")


def _parse_declaration(
    line: str,
) -> tuple[list[str], str | None, str]:
    """Parse flags, an optional argument specification, and inline description."""
    stripped = line.strip()

    # Find the first argument specification, if present.
    argument_match = ARGUMENT_RE.search(stripped)

    if argument_match:
        declaration_end = argument_match.end()
        declaration = stripped[:declaration_end]

        # Everything after the argument is the inline description.
        inline_description = stripped[declaration_end:].strip()
    else:
        # Without an argument, use the normal two-column spacing to
        # separate the declaration from its inline description.
        parts = re.split(r"\s{2,}", stripped, maxsplit=1)
        declaration = parts[0]
        inline_description = parts[1].strip() if len(parts) > 1 else ""

    argument = (
        argument_match.group(0)
        if argument_match
        else None
    )

    # Extract flags only from the declaration portion.
    flag_text = (
        declaration[:argument_match.start()]
        if argument_match
        else declaration
    )

    flags = FLAG_RE.findall(flag_text)

    return flags, argument, inline_description


def parse_cli_help(
    file_path: Path,
    tool_name: str = "HandBrakeCLI",
) -> list[CLIOption]:
    """Parse HandBrakeCLI help output into deterministic evidence facts."""
    text = file_path.read_text(encoding="utf-8")
    source_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    lines = text.splitlines()

    blocks: list[dict] = []
    current_block: dict | None = None
    current_section: str | None = None

    # Group each option declaration with its complete multiline description.
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if SECTION_RE.match(stripped):
            if current_block is not None:
                blocks.append(current_block)
                current_block = None
            current_section = stripped.split("----")[0].strip()
            continue

        if DECLARATION_LINE_RE.match(line):
            if current_block is not None:
                blocks.append(current_block)

            current_block = {
                "start_line": line_number,
                "end_line": line_number,
                "declaration_line": line,
                "description_lines": [],
                "section": current_section,
            }
            continue

        if current_block is None:
            continue

        if not stripped:
            blocks.append(current_block)
            current_block = None
            continue

        current_block["description_lines"].append(stripped)
        current_block["end_line"] = line_number

    if current_block is not None:
        blocks.append(current_block)

    options: list[CLIOption] = []

    for block in blocks:
        flags, argument, inline_description = _parse_declaration(
            block["declaration_line"]
        )

        if not flags:
            continue

        description_lines: list[str] = []

        if inline_description:
            description_lines.append(inline_description)

        description_lines.extend(block["description_lines"])

        description = "\n".join(description_lines).strip() or None

        long_flags = [
            flag for flag in flags
            if flag.startswith("--")
        ]
        short_flags = [
            flag for flag in flags
            if not flag.startswith("--")
        ]

        source_id = f"{file_path.name}#L{block['start_line']}"

        # Multiple long options on one declaration line represent
        # independent options, not aliases.
        if len(long_flags) > 1:
            for long_flag in long_flags:
                options.append(
                    CLIOption(
                        name=long_flag,
                        description=description,
                        aliases=[],
                        argument=argument,
                        section=block["section"],
                        source_id=source_id,
                        source_sha256=source_sha256,
                        parent_command=None,
                        line_start=block["start_line"],
                        line_end=block["end_line"],
                        tool=tool_name,
                    )
                )
            continue

        # A single long option may have one or more short aliases.
        primary_name = (
            long_flags[0]
            if long_flags
            else short_flags[0]
        )

        aliases = short_flags if long_flags else []

        options.append(
            CLIOption(
                name=primary_name,
                description=description,
                aliases=aliases,
                argument=argument,
                section=block["section"],
                source_id=source_id,
                source_sha256=source_sha256,
                parent_command=None,
                line_start=block["start_line"],
                line_end=block["end_line"],
                tool=tool_name,
            )
        )

    return options
