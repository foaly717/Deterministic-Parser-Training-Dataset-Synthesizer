import re

from dataset_tools.evidence.index import EvidenceIndex


# Updated regex: Includes underscores (_) alongside hyphens (-)
OPTION_RE = re.compile(r"(?<!\S)--?[A-Za-z0-9][A-Za-z0-9_-]*")


def validate_cli_response(
    response: str,
    evidence_index: EvidenceIndex,
) -> tuple[bool, str]:
    """Validate that CLI options exist in supplied evidence."""

    raw_tokens = response.split()
    extracted_flags = set()

    for token in raw_tokens:
        # Strip values attached with '=' (e.g., --preset=Fast -> --preset)
        flag_candidate = token.split("=")[0]
        match = OPTION_RE.match(flag_candidate)
        if match:
            extracted_flags.add(match.group(0))

    if not extracted_flags:
        return True, "No CLI flags detected in response."

    invalid_flags = extracted_flags - evidence_index.valid_options

    if invalid_flags:
        return (
            False,
            f"Unsupported options detected: {sorted(invalid_flags)}",
        )

    return True, "All detected options are supported by supplied evidence."
