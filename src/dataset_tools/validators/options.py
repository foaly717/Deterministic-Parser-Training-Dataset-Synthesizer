import re

from dataset_tools.evidence.index import EvidenceIndex


OPTION_RE = re.compile(r"(?<!\S)--?[A-Za-z0-9][A-Za-z0-9-]*")


def validate_cli_response(
    response: str,
    evidence_index: EvidenceIndex,
) -> tuple[bool, str]:
    """Validate that CLI options exist in supplied evidence."""

    extracted_flags = set(OPTION_RE.findall(response))

    if not extracted_flags:
        return True, "No CLI flags detected in response."

    invalid_flags = (
        extracted_flags - evidence_index.valid_options
    )

    if invalid_flags:
        return (
            False,
            f"Unsupported options detected: {sorted(invalid_flags)}",
        )

    return True, "All detected options are supported by supplied evidence."
