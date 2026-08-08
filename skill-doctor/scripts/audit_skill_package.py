#!/usr/bin/env python3
"""Deterministic, read-only structural auditor for an Agent Skill package.

Exit codes:
  0: no FAIL findings (WARN may exist)
  1: one or more FAIL findings
  2: invocation or dependency error

This script produces structural evidence only. Semantic quality and authorization
boundaries still require Agent review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - exercised through a subprocess in deployment
    yaml = None

EXPECTED_DIMENSIONS = {
    1: "必要性",
    2: "触发正面",
    3: "触发覆盖面",
    4: "负触发",
    5: "冲突规则",
    6: "输入要求",
    7: "工作流",
    8: "输出格式",
    9: "质量标准与验证闭环",
    10: "简洁性",
    11: "硬规则 vs Checklist",
    12: "日志与可观测性",
}

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*```(?P<lang>[A-Za-z0-9_+.-]*)\s*$")
DIMENSION_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*\*\*([^*]+)\*\*\s*\|", re.MULTILINE)
SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[\"']?([A-Za-z0-9_./+\-=]{12,})"
)
PLACEHOLDER_RE = re.compile(
    r"(?i)(redacted|placeholder|example|your[_-]|dummy|fake|sample|\*\*\*|<[^>]+>|\$\{)"
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    line: int
    message: str


def log(level: str, message: str, *, enabled: bool) -> None:
    if not enabled:
        return
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"{stamp} {level} {message}", file=sys.stderr)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def strip_code(text: str) -> str:
    """Remove fenced and inline code so documentation examples are not dependencies."""
    output: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if FENCE_RE.match(line.rstrip("\n")):
            in_fence = not in_fence
            output.append("\n")
            continue
        if in_fence:
            output.append("\n")
            continue
        output.append(re.sub(r"`[^`\n]*`", "", line))
    return "".join(output)


def iter_fenced_blocks(text: str) -> Iterable[tuple[str, str, int]]:
    lang = ""
    start = 0
    lines: list[str] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE_RE.match(line)
        if match:
            if not in_fence:
                in_fence = True
                lang = match.group("lang").lower()
                start = number
                lines = []
            else:
                yield lang, "\n".join(lines) + "\n", start
                in_fence = False
            continue
        if in_fence:
            lines.append(line)


def package_hash(root: Path, files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        digest.update(str(path.relative_to(root)).encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def audit(root: Path, *, verbose: bool = False) -> dict:
    root = root.resolve()
    findings: list[Finding] = []

    def add(severity: str, code: str, path: str, line: int, message: str) -> None:
        findings.append(Finding(severity, code, path, line, message))

    if not root.is_dir():
        raise ValueError(f"Skill root is not a directory: {root}")
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        raise ValueError(f"Missing SKILL.md under: {root}")

    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and not path.name.startswith(".")
    )
    log("INFO", f"scanning {len(files)} files under {root}", enabled=verbose)

    markdown_files = [path for path in files if path.suffix.lower() == ".md"]
    for path in markdown_files:
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8")
        fence_lines = [
            number for number, line in enumerate(text.splitlines(), 1)
            if FENCE_RE.match(line)
        ]
        if len(fence_lines) % 2:
            add("FAIL", "markdown.unbalanced_fence", rel, fence_lines[-1], "Unbalanced Markdown code fence")

        clean_text = strip_code(text)
        for match in LINK_RE.finditer(clean_text):
            target = match.group(1).strip().split()[0].split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                add(
                    "FAIL",
                    "markdown.broken_link",
                    rel,
                    line_number(clean_text, match.start()),
                    f"Missing relative link target: {target}",
                )

        for match in SECRET_RE.finditer(clean_text):
            value = match.group(2)
            context = clean_text[max(0, match.start() - 50): match.end() + 50]
            if not PLACEHOLDER_RE.search(value) and not PLACEHOLDER_RE.search(context):
                add(
                    "WARN",
                    "security.secret_lead",
                    rel,
                    line_number(clean_text, match.start()),
                    "Possible credential-like value; semantic review required",
                )

        for lang, block, start_line in iter_fenced_blocks(text):
            if not block.strip():
                add("WARN", "markdown.empty_fence", rel, start_line, "Empty code block")
            if lang in {"bash", "sh", "shell"}:
                result = subprocess.run(
                    ["bash", "-n"], input=block, text=True, capture_output=True, check=False
                )
                if result.returncode != 0:
                    add(
                        "FAIL",
                        "shell.syntax",
                        rel,
                        start_line,
                        result.stderr.strip() or "bash -n failed",
                    )

    skill_text = skill_md.read_text(encoding="utf-8")
    skill_lines = len(skill_text.splitlines())
    skill_bytes = len(skill_text.encode("utf-8"))
    if skill_lines > 300:
        add("FAIL", "size.main_lines", "SKILL.md", 1, f"SKILL.md has {skill_lines} lines (>300)")
    elif skill_lines > 220:
        add("WARN", "size.main_lines", "SKILL.md", 1, f"SKILL.md has {skill_lines} lines (>220 target)")
    if skill_bytes > 25_000:
        add("WARN", "size.main_bytes", "SKILL.md", 1, f"SKILL.md has {skill_bytes} bytes (>25000 target)")

    if not skill_text.startswith("---\n") or "\n---\n" not in skill_text[4:]:
        add("FAIL", "frontmatter.missing", "SKILL.md", 1, "Missing YAML frontmatter")
        metadata = {}
    elif yaml is None:
        add("FAIL", "dependency.pyyaml", "SKILL.md", 1, "PyYAML is required for frontmatter validation")
        metadata = {}
    else:
        frontmatter = skill_text.split("---", 2)[1]
        try:
            metadata = yaml.safe_load(frontmatter) or {}
            if not isinstance(metadata, dict):
                raise TypeError("frontmatter must be a mapping")
        except Exception as exc:  # noqa: BLE001 - error becomes structured evidence
            add("FAIL", "frontmatter.invalid", "SKILL.md", 1, f"Invalid YAML frontmatter: {exc}")
            metadata = {}

    for key in ("name", "description"):
        if not metadata.get(key):
            add("FAIL", f"frontmatter.missing_{key}", "SKILL.md", 1, f"Missing frontmatter field: {key}")
    description = metadata.get("description", "")
    if isinstance(description, str) and len(description) > 250:
        add(
            "FAIL",
            "frontmatter.description_length",
            "SKILL.md",
            1,
            f"Description has {len(description)} characters (>250)",
        )

    dimensions: dict[int, str] = {}
    duplicate_ids: list[int] = []
    for raw_id, raw_name in DIMENSION_RE.findall(skill_text):
        dim_id = int(raw_id)
        if dim_id in dimensions:
            duplicate_ids.append(dim_id)
        dimensions[dim_id] = raw_name.strip()
    if duplicate_ids:
        add("FAIL", "dimensions.duplicate", "SKILL.md", 1, f"Duplicate dimension IDs: {sorted(set(duplicate_ids))}")
    if dimensions != EXPECTED_DIMENSIONS:
        add(
            "FAIL",
            "dimensions.drift",
            "SKILL.md",
            1,
            f"Dimension mapping drift: expected {EXPECTED_DIMENSIONS}, got {dimensions}",
        )

    clean_main = strip_code(skill_text)
    reference_links = {
        match.group(1).strip().split()[0].split("#", 1)[0]
        for match in LINK_RE.finditer(clean_main)
        if match.group(1).strip().startswith("references/")
    }
    if len(reference_links) > 10:
        add(
            "WARN",
            "references.too_many",
            "SKILL.md",
            1,
            f"SKILL.md links {len(reference_links)} references (>10); review consolidation",
        )

    for path in files:
        if path.suffix.lower() != ".py":
            continue
        rel = str(path.relative_to(root))
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as exc:
            add("FAIL", "python.syntax", rel, exc.lineno or 1, str(exc))

    severity_counts = {
        severity: sum(item.severity == severity for item in findings)
        for severity in ("FAIL", "WARN")
    }
    result = {
        "schema_version": 1,
        "root": str(root),
        "package_sha256": package_hash(root, files),
        "inventory": {
            "file_count": len(files),
            "markdown_count": len(markdown_files),
            "skill_lines": skill_lines,
            "skill_bytes": skill_bytes,
            "linked_reference_count": len(reference_links),
        },
        "status": "FAIL" if severity_counts["FAIL"] else ("WARN" if severity_counts["WARN"] else "PASS"),
        "counts": severity_counts,
        "findings": [asdict(item) for item in findings],
        "scope_note": "Structural evidence only; semantic review remains mandatory.",
    }
    log("INFO", f"status={result['status']} counts={severity_counts}", enabled=verbose)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def render_text(result: dict) -> str:
    lines = [
        f"status: {result['status']}",
        f"root: {result['root']}",
        f"package_sha256: {result['package_sha256']}",
        f"files: {result['inventory']['file_count']}",
        f"FAIL: {result['counts']['FAIL']}",
        f"WARN: {result['counts']['WARN']}",
    ]
    for finding in result["findings"]:
        lines.append(
            f"[{finding['severity']}] {finding['code']} "
            f"{finding['path']}:{finding['line']} — {finding['message']}"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        result = audit(Path(args.root), verbose=args.verbose)
    except (OSError, ValueError) as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_text(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 1 if result["counts"]["FAIL"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
