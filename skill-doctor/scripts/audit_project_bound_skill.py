#!/usr/bin/env python3
"""Mechanical gate for a repository-bound software maintenance Skill."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

REPO_REQUIRED = (
    "AGENTS.md",
    "PROJECT.yaml",
    "README.md",
    "docs/index.md",
    "scripts/project_doctor.py",
)
SKILL_POINTERS = (
    "AGENTS.md",
    "PROJECT.yaml",
    "docs/index.md",
    "project_doctor.py",
)


def longest_numbered_run(value: str) -> int:
    longest = current = 0
    for line in value.splitlines():
        if re.match(r"^\d+\. ", line):
            current += 1
            longest = max(longest, current)
        elif line.strip():
            current = 0
    return longest


def audit(skill_dir: Path, repo_dir: Path) -> dict:
    fail: list[str] = []
    warn: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail.append("skill missing SKILL.md")
        skill = ""
    else:
        skill = skill_file.read_text(encoding="utf-8", errors="replace")

    if not (repo_dir / ".git").exists():
        fail.append("repository missing .git")
    for rel in REPO_REQUIRED:
        if not (repo_dir / rel).is_file():
            fail.append(f"repository contract missing: {rel}")

    for pointer in SKILL_POINTERS:
        if pointer not in skill:
            fail.append(f"Skill does not route to repository contract: {pointer}")

    repo_authority_phrases = ("GitHub", "权威", "仓库")
    if not all(token in skill for token in repo_authority_phrases):
        warn.append("Skill does not clearly declare repository authority")
    if "PROJECT_CONTRACT_DRIFT" not in skill and "fail closed" not in skill:
        warn.append("Skill lacks repository-contract drift blocking semantics")

    skill_lines = len(skill.splitlines())
    if skill_lines > 180:
        warn.append(f"Skill remains large after repository contract exists: {skill_lines} lines")

    duplicate_markers = {
        "formula_block": len(re.findall(r"(?m)^(?:F|H|J|AD|AL|AO|AP|AR|AS|AT)\s*=", skill)),
        "api_inventory": len(re.findall(r"`(?:GET|POST|PUT|DELETE) /api/", skill)),
        "longest_numbered_rule_run": longest_numbered_run(skill),
    }
    if duplicate_markers["formula_block"] >= 3:
        warn.append("Skill appears to duplicate project formula definitions")
    if duplicate_markers["api_inventory"] >= 5:
        warn.append("Skill appears to duplicate an API inventory")
    if duplicate_markers["longest_numbered_rule_run"] >= 15:
        warn.append("Skill appears to retain a long project-rule catalogue")

    secret_patterns = (r"sk-[A-Za-z0-9_-]{16,}", r"ghp_[A-Za-z0-9]{20,}")
    if any(re.search(pattern, skill) for pattern in secret_patterns):
        fail.append("Skill contains a credential-like value")

    return {
        "schema_version": 1,
        "status": "FAIL" if fail else ("WARN" if warn else "PASS"),
        "failures": fail,
        "warnings": warn,
        "evidence": {
            "skill_lines": skill_lines,
            "repo_contract_files": sum((repo_dir / rel).is_file() for rel in REPO_REQUIRED),
            "duplicate_markers": duplicate_markers,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-dir", type=Path, required=True)
    parser.add_argument("--repo-dir", type=Path, required=True)
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    result = audit(args.skill_dir.resolve(), args.repo_dir.resolve())
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for item in result["failures"]:
            print(f"FAIL: {item}")
        for item in result["warnings"]:
            print(f"WARN: {item}")
    return 1 if result["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
