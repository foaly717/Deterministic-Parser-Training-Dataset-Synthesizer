#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    options = Counter()
    statuses = Counter()
    total = 0

    with args.input.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            total += 1
            statuses[record["validation"]["status"]] += 1

            parsed = record.get("parsed")
            if not isinstance(parsed, dict):
                continue

            response = parsed.get("response", "")
            for token in response.split():
                if token.startswith("-"):
                    options[token] += 1

    print("=== DATASET COVERAGE REPORT ===")
    print(f"Records: {total}")
    print()
    print("Statuses:")
    for key, value in statuses.items():
        print(f"  {key}: {value}")
    print()
    print("Observed flags:")
    for key, value in options.most_common():
        print(f"  {key}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
