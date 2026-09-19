import shlex

from dataset_tools.parsers.command import (
    ParsedCommand,
    ParsedOption,
)


class CLIParseError(ValueError):
    """Raised when CLI text cannot be normalized."""


def parse_cli_command(response: str) -> ParsedCommand:
    """Parse a single CLI command into normalized IR.

    Supports:
      --flag
      --flag value
      --flag=value
    """

    tokens = shlex.split(response.strip())

    if not tokens:
        raise CLIParseError("Command cannot be empty.")

    executable = tokens[0]
    options: list[ParsedOption] = []

    index = 1

    while index < len(tokens):
        token = tokens[index]

        if not token.startswith("-"):
            index += 1
            continue

        if "=" in token:
            name, value = token.split("=", 1)
            options.append(
                ParsedOption(
                    name=name,
                    value=value,
                )
            )
            index += 1
            continue

        value = None

        if (
            index + 1 < len(tokens)
            and not tokens[index + 1].startswith("-")
        ):
            value = tokens[index + 1]
            index += 1

        options.append(
            ParsedOption(
                name=token,
                value=value,
            )
        )

        index += 1

    return ParsedCommand(
        executable=executable,
        options=tuple(options),
    )
