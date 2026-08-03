#!/usr/bin/env python3
"""Validate CS2 behavior-tree .kv3 files.

Checks, per file:
  - the KV3 encoding header comment is present
  - braces/parens/brackets are balanced (ignoring strings and //, /* */ comments)

Usage:
  py check_kv3.py [path...]      # default: check all .kv3 under the repo's ai root
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# The KV3 encoding header every .kv3 behavior-tree file starts with.
KV3_HEADER = "<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->"

# Strip block comments, line comments, and string literals so we only tokenize code.
_BLOCK_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_RE = re.compile(r"//[^\n]*")
_STRING_RE = re.compile(r'"(?:[^"\\]|\\.)*"')


def strip_comments_and_strings(text: str) -> str:
    text = _BLOCK_RE.sub("", text)
    text = _STRING_RE.sub('""', text)  # replace strings with balanced empty quotes
    text = _LINE_RE.sub("", text)
    return text


def check_balance(path: Path) -> list[str]:
    text = strip_comments_and_strings(path.read_text(encoding="utf-8-sig"))
    stack: list[str] = []
    pairs = {")": "(", "]": "[", "}": "{"}
    errors: list[str] = []
    for i, ch in enumerate(text):
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack[-1] != pairs[ch]:
                errors.append(f"  line {text.count(chr(10), 0, i) + 1}: unmatched {ch!r}")
                # keep going, don't pop the wrong opener
                continue
            stack.pop()
    if stack:
        for ch in stack:
            errors.append(f"  unclosed {ch!r}")
    return errors


def main() -> None:
    repo = Path(__file__).resolve().parent
    args = [Path(a).resolve() for a in sys.argv[1:]] or [repo]
    targets: list[Path] = []
    for a in args:
        if a.is_dir():
            targets.extend(sorted(a.rglob("*.kv3")))
        elif a.is_file():
            targets.append(a)

    if not targets:
        print("No .kv3 files found.")
        sys.exit(1)

    problems = 0
    for path in targets:
        rel = path.relative_to(repo) if repo in path.parents else path
        text = path.read_text(encoding="utf-8-sig")
        file_errors: list[str] = []
        if KV3_HEADER not in text:
            file_errors.append("  missing KV3 header")
        file_errors.extend(check_balance(path))
        if not file_errors:
            print(f"OK   {rel}")
        else:
            problems += 1
            print(f"FAIL {rel}")
            for e in file_errors:
                print(e)

    print(f"\n{len(targets)} files checked, {problems} problem(s).")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
