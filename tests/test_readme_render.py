"""Test that README.md results block matches a fresh render from results/summary/*.json."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.render_readme import render_readme  # noqa: E402


def test_readme_render_up_to_date():
    exit_code = render_readme(REPO_ROOT, check=True)
    assert exit_code == 0, (
        "README.md results block is out of date. "
        "Run 'python scripts/render_readme.py' to update it."
    )
