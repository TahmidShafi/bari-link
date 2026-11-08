"""Verify that all relative markdown links in README.md and docs/*.md resolve to existing files.

Usage:
    python scripts/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Matches markdown links [text](target) but ignores images ![alt](url) or handles them too
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


def check_file_links(file_path: Path, repo_root: Path) -> list[str]:
    errors = []
    content = file_path.read_text(encoding="utf-8")

    # Ignore fenced code blocks
    lines = []
    in_code_block = False
    for line in content.splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            lines.append(line)
    clean_text = "\n".join(lines)

    for match in LINK_RE.finditer(clean_text):
        target = match.group(2).strip()

        # Skip external URLs, mailto, and pure in-page anchors
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue

        # Strip anchor if present
        clean_target = target.split("#")[0]
        if not clean_target:
            continue

        # Resolve relative to the markdown file's directory
        resolved_path = (file_path.parent / clean_target).resolve()

        if not resolved_path.exists():
            rel = file_path.relative_to(repo_root)
            errors.append(f"{rel}: Link '{target}' -> '{resolved_path}' NOT FOUND")

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    md_files = [repo_root / "README.md", repo_root / "PROJECT_CONTEXT.md"]
    docs_dir = repo_root / "docs"
    if docs_dir.exists():
        md_files.extend(docs_dir.rglob("*.md"))

    all_errors = []
    for md_file in md_files:
        if md_file.exists():
            errors = check_file_links(md_file, repo_root)
            all_errors.extend(errors)

    if all_errors:
        print("Link check FAILED with errors:", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"All relative links in {len(md_files)} markdown files resolved successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
