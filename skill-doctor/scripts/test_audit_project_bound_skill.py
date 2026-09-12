#!/usr/bin/env python3
"""Tests for audit_project_bound_skill.py."""
from pathlib import Path
import tempfile

from audit_project_bound_skill import audit, REPO_REQUIRED


def make_valid(root: Path) -> tuple[Path, Path]:
    skill = root / "skill"
    repo = root / "repo"
    skill.mkdir()
    (repo / ".git").mkdir(parents=True)
    for rel in REPO_REQUIRED:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("placeholder\n", encoding="utf-8")
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: demo\n---\n"
        "GitHub仓库是权威源。先读AGENTS.md、PROJECT.yaml、docs/index.md，"
        "运行project_doctor.py；缺失时PROJECT_CONTRACT_DRIFT并fail closed。\n",
        encoding="utf-8",
    )
    return skill, repo


def test_valid_package_passes():
    with tempfile.TemporaryDirectory() as tmp:
        skill, repo = make_valid(Path(tmp))
        result = audit(skill, repo)
        assert result["status"] == "PASS", result


def test_missing_repository_contract_fails():
    with tempfile.TemporaryDirectory() as tmp:
        skill, repo = make_valid(Path(tmp))
        (repo / "AGENTS.md").unlink()
        result = audit(skill, repo)
        assert result["status"] == "FAIL"
        assert "repository contract missing: AGENTS.md" in result["failures"]


def test_large_rule_catalogue_warns():
    with tempfile.TemporaryDirectory() as tmp:
        skill, repo = make_valid(Path(tmp))
        path = skill / "SKILL.md"
        path.write_text(path.read_text() + "\n".join(f"{i}. rule" for i in range(1, 20)), encoding="utf-8")
        result = audit(skill, repo)
        assert result["status"] == "WARN"
        assert any("rule catalogue" in item for item in result["warnings"])


if __name__ == "__main__":
    test_valid_package_passes()
    test_missing_repository_contract_fails()
    test_large_rule_catalogue_warns()
    print("PASS: 3 project-bound Skill gate tests")
