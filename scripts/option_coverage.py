#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path

from dataset_tools.parsers.cli_help import parse_cli_help




def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    documented = {
        fact.name
        for fact in parse_cli_help(args.evidence)
        if fact.name.startswith("-")
    }

    observed = Counter()

    with args.input.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            parsed = record.get("parsed")
            if not isinstance(parsed, dict):
                continue

            for token in parsed.get("response", "").split():
                if token.startswith("-"):
                    observed[token] += 1

    covered = set(observed)
    uncovered = sorted(documented - covered)

    print("=== OPTION COVERAGE REPORT ===")
    print(f"Documented options: {len(documented)}")
    print(f"Observed options:   {len(covered)}")
    print(f"Coverage:           {len(covered & documented) / len(documented):.1%}")
    print()
    print("Observed:")
    for option, count in observed.most_common():
        print(f"  {option}: {count}")
    print()
    print("Uncovered:")
    for option in uncovered:
        print(f"  {option}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
