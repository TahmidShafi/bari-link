"""Query git log to extract verifiable pre-registration commit SHAs and outcome commits.

Writes results/summary/preregistration.json for render_readme.py to consume.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path


def get_git_commit(
    search_phrase: str, file_path: str = "PROJECT_CONTEXT.md", first: bool = True
) -> dict[str, str]:
    """Find the commit that introduced (or modified) a search phrase in git history."""
    cmd = [
        "git",
        "log",
        "-S",
        search_phrase,
        "--date=iso",
        "--pretty=format:%H|%h|%ad|%s",
        "--",
        file_path,
    ]
    res = subprocess.check_output(cmd, text=True).strip()
    if not res:
        raise ValueError(f"No commit found for search phrase: {search_phrase}")

    lines = [line.strip() for line in res.splitlines() if line.strip()]
    selected_line = lines[-1] if first else lines[0]
    full_sha, short_sha, date_str, subject = selected_line.split("|", 3)
    return {
        "full_sha": full_sha,
        "short_sha": short_sha,
        "date": date_str,
        "subject": subject,
    }


def generate_preregistration_summary(
    output_path: str | Path = "results/summary/preregistration.json",
) -> dict:
    output_path = Path(output_path)

    # 1. H1
    h1_prereg = get_git_commit(
        "Missed duplicates are concentrated in pairs whose guardian fields "
        "refer to different relationships",
        first=True,
    )
    h1_outcome = get_git_commit("Outcome of Hypothesis H1", first=True)

    # 2. H2
    h2_prereg = get_git_commit("Roster overlap identifies households, not persons", first=True)
    h2_outcome = get_git_commit("Outcome of Hypothesis H2", first=True)

    # 3. H3
    h3_prereg = get_git_commit(
        "Kinship evidence should act as deterministic constraints, "
        "not as probabilistic Fellegi-Sunter evidence",
        first=True,
    )
    h3_outcome = get_git_commit(
        "Fresh Holdout Confirmation (`holdout_5` .. `holdout_9`)", first=True
    )

    # 4. Data leakage
    leakage = get_git_commit(
        "Pre-implementation schema audit discovered ground-truth attribute leakage",
        first=True,
    )

    # Verify chronological ordering (prereg strictly precedes outcome)
    dt_fmt = "%Y-%m-%d %H:%M:%S %z"
    for name, p, o in [
        ("H1", h1_prereg, h1_outcome),
        ("H2", h2_prereg, h2_outcome),
        ("H3", h3_prereg, h3_outcome),
    ]:
        p_dt = datetime.strptime(p["date"], dt_fmt)
        o_dt = datetime.strptime(o["date"], dt_fmt)
        assert p_dt < o_dt, (
            f"{name} pre-registration date ({p_dt}) does not precede outcome date ({o_dt})!"
        )

    data = {
        "source": "results/summary/preregistration.json",
        "description": "Git-verified commit SHAs for pre-registered hypotheses and data leakage",
        "leakage": {
            "title": "Ground-Truth Data Leakage Discovery & Remediation",
            "commit": leakage["short_sha"],
            "full_sha": leakage["full_sha"],
            "date": leakage["date"],
            "subject": leakage["subject"],
        },
        "h1": {
            "title": "H1: Guardian Type Disambiguation (Model v2)",
            "prereg_commit": h1_prereg["short_sha"],
            "prereg_full_sha": h1_prereg["full_sha"],
            "prereg_date": h1_prereg["date"],
            "prereg_subject": h1_prereg["subject"],
            "outcome_commit": h1_outcome["short_sha"],
            "outcome_full_sha": h1_outcome["full_sha"],
            "outcome_date": h1_outcome["date"],
            "outcome_subject": h1_outcome["subject"],
            "precedes_outcome": True,
        },
        "h2": {
            "title": "H2: Household vs Individual Kinship Disambiguation (Model v3)",
            "prereg_commit": h2_prereg["short_sha"],
            "prereg_full_sha": h2_prereg["full_sha"],
            "prereg_date": h2_prereg["date"],
            "prereg_subject": h2_prereg["subject"],
            "outcome_commit": h2_outcome["short_sha"],
            "outcome_full_sha": h2_outcome["full_sha"],
            "outcome_date": h2_outcome["date"],
            "outcome_subject": h2_outcome["subject"],
            "precedes_outcome": True,
        },
        "h3": {
            "title": "H3: Kinship as Deterministic Constraint (Pipeline K)",
            "prereg_commit": h3_prereg["short_sha"],
            "prereg_full_sha": h3_prereg["full_sha"],
            "prereg_date": h3_prereg["date"],
            "prereg_subject": h3_prereg["subject"],
            "outcome_commit": h3_outcome["short_sha"],
            "outcome_full_sha": h3_outcome["full_sha"],
            "outcome_date": h3_outcome["date"],
            "outcome_subject": h3_outcome["subject"],
            "precedes_outcome": True,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Pre-registration summary written to: {output_path}")
    print("\nVerified Pre-Registration and Outcome Commits:")
    print(f"  Leakage: {leakage['short_sha']} ({leakage['date']}) - {leakage['subject']}")
    print(
        f"  H1:      Prereg {h1_prereg['short_sha']} ({h1_prereg['date']}) -> "
        f"Outcome {h1_outcome['short_sha']} ({h1_outcome['date']})"
    )
    print(
        f"  H2:      Prereg {h2_prereg['short_sha']} ({h2_prereg['date']}) -> "
        f"Outcome {h2_outcome['short_sha']} ({h2_outcome['date']})"
    )
    print(
        f"  H3:      Prereg {h3_prereg['short_sha']} ({h3_prereg['date']}) -> "
        f"Outcome {h3_outcome['short_sha']} ({h3_outcome['date']})"
    )

    return data


if __name__ == "__main__":
    generate_preregistration_summary()
