#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    decoder = json.JSONDecoder()

    for n, line in enumerate(
        args.input.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = line.strip()
        if not line:
            continue

        pos = 0
        records_in_line = []

        while pos < len(line):
            while pos < len(line) and line[pos].isspace():
                pos += 1
            if pos >= len(line):
                break

            try:
                obj, end = decoder.raw_decode(line, pos)
                records_in_line.append(obj)
                pos = end
            except json.JSONDecodeError:
                print(
                    f"[Line {n}] Unparseable tail starting at char {pos}: "
                    f"{line[pos:pos+100]!r}"
                )
                break

        print(f"Line {n}: Parsed {len(records_in_line)} object(s).")
        for record in records_in_line:
            print(
                f"  Attempt: {record.get('attempt')} | "
                f"Status: {record.get('status')} | "
                f"Validation: {record.get('validation')}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
