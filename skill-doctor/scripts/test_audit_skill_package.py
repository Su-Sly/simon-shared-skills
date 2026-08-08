#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("audit_skill_package.py")
SPEC = importlib.util.spec_from_file_location("audit_skill_package", MODULE_PATH)
assert SPEC and SPEC.loader
AUDITOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDITOR
SPEC.loader.exec_module(AUDITOR)

DIMENSIONS = [
    "必要性",
    "触发正面",
    "触发覆盖面",
    "负触发",
    "冲突规则",
    "输入要求",
    "工作流",
    "输出格式",
    "质量标准与验证闭环",
    "简洁性",
    "硬规则 vs Checklist",
    "日志与可观测性",
]


def skill_text(*, description: str = "Use when reviewing a Skill.", extra: str = "") -> str:
    rows = "\n".join(
        f"| {index} | **{name}** | check |"
        for index, name in enumerate(DIMENSIONS, 1)
    )
    return (
        "---\n"
        "name: fixture-skill\n"
        f'description: "{description}"\n'
        "version: 1.0.0\n"
        "---\n\n"
        "# Fixture Skill\n\n"
        "| # | 维度 | 检查 |\n"
        "|---|---|---|\n"
        f"{rows}\n\n"
        "[Reference](references/guide.md)\n"
        f"{extra}\n"
    )


class AuditSkillPackageTests(unittest.TestCase):
    def make_package(self, *, main: str | None = None) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / "references").mkdir()
        (root / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        (root / "SKILL.md").write_text(main or skill_text(), encoding="utf-8")
        return root

    def codes(self, result: dict) -> set[str]:
        return {finding["code"] for finding in result["findings"]}

    def test_valid_package_passes(self) -> None:
        result = AUDITOR.audit(self.make_package())
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["counts"], {"FAIL": 0, "WARN": 0})

    def test_broken_relative_link_fails(self) -> None:
        root = self.make_package(main=skill_text().replace("guide.md", "missing.md"))
        result = AUDITOR.audit(root)
        self.assertIn("markdown.broken_link", self.codes(result))
        self.assertEqual(result["status"], "FAIL")

    def test_code_examples_are_not_treated_as_dependencies(self) -> None:
        extra = "Inline example: `[x](references/missing.md)`\n\n```markdown\n[x](references/also-missing.md)\n```"
        result = AUDITOR.audit(self.make_package(main=skill_text(extra=extra)))
        self.assertNotIn("markdown.broken_link", self.codes(result))

    def test_unbalanced_fence_fails(self) -> None:
        result = AUDITOR.audit(self.make_package(main=skill_text(extra="```bash\necho ok")))
        self.assertIn("markdown.unbalanced_fence", self.codes(result))

    def test_long_description_fails(self) -> None:
        result = AUDITOR.audit(self.make_package(main=skill_text(description="x" * 251)))
        self.assertIn("frontmatter.description_length", self.codes(result))

    def test_dimension_drift_fails(self) -> None:
        changed = skill_text().replace("| 12 | **日志与可观测性**", "| 13 | **日志与可观测性**")
        result = AUDITOR.audit(self.make_package(main=changed))
        self.assertIn("dimensions.drift", self.codes(result))

    def test_invalid_yaml_fails(self) -> None:
        changed = skill_text().replace('description: "Use when reviewing a Skill."', "description: [unterminated")
        result = AUDITOR.audit(self.make_package(main=changed))
        self.assertIn("frontmatter.invalid", self.codes(result))


if __name__ == "__main__":
    unittest.main(verbosity=2)
