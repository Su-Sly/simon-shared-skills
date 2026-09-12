#!/usr/bin/env python3
"""Cross-skill overlap probe: identity-token grep, no similarity scoring.

Extracts identity tokens (script names, env vars, dotted config keys,
watchdog/cron names, hermes subcommands, distinctive paths) from the target
skill and from every other SKILL.md frontmatter + scripts inventory in the
library, then greps both directions and prints a counts-only JSON matrix.

Zero LLM tokens: all extraction and matching happens here. Semantic verdicts
(CANONICAL_*/DUPLICATE_MIGRATE/STALE_INSTRUCTION/FALSE_POSITIVE) belong to the
auditing agent per the overlap_assessment contract (skill-doctor v3.9.0).

Usage:
    check_cross_skill_overlap.py TARGET_ROOT [--lib LIB_ROOT] [--json]
    check_cross_skill_overlap.py --batch LIB_ROOT [--json]

Exit codes: 0 = ran, findings may exist; 2 = usage/IO error.
Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

MIN_TOKEN_LEN = 6
THRESHOLD = 2  # distinct tokens required before a candidate is surfaced

GENERIC_TOKENS = {
    "config.yaml", ".env", "gateway.log", "backup", "backups", "skill.md",
    "references", "scripts", "cronjob", "telegram", "hermes", "profile",
    "profiles", "read_file", "write_file", "search_files", "web_search",
    "web_extract", "terminal", "AGENTS.md", "PROJECT.md", "SKILL_DOCTOR",
    "LOG_LEVEL", "UTF-8", "STDOUT", "STDERR", "API_KEY", "sqlite3.connect",
    "jobs.json", "state.db",
}

# stdlib/idiom noise: these appear in nearly every coding skill
CODE_IDIOM_RE = re.compile(r"^(?:os|sys|re|json|time|pathlib|subprocess|logging)\.\w+\.\w+$")

# doc-style names (anything.md) and bare shallow paths are noise by construction
def _is_noise(tok: str) -> bool:
    if tok.lower().endswith(".md"):
        return True
    if tok.startswith(("~", "$HOME", "/Users/")):
        parts = [p for p in tok.replace("$HOME", "").replace("/Users/simon", "").split("/") if p]
        meaningful = [p for p in parts if p not in {".hermes", "logs", "profiles", "skills", "scripts", "cache"}]
        return len(meaningful) < 2  # need e.g. logs/gateway.log, scripts/web-search-watchdog.py
    return bool(CODE_IDIOM_RE.match(tok))

TOKEN_PATTERNS = [
    ("script", re.compile(r"[\w./-]+(?:-[\w.]+)+\.(?:py|sh|js|ts)\b")),
    ("env", re.compile(r"\b[A-Z][A-Z0-9]{5,}_[A-Z0-9_]+\b")),
    ("cfgkey", re.compile(r"\b[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]+){2,}\b")),
    ("path", re.compile(r"(?:~|\$HOME|/Users/[\w.]+)[\w./-]{5,}")),
]


def strip_code(text: str) -> str:
    out, fence = [], False
    for line in text.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            fence = not fence
            continue
        if not fence:
            out.append(line)
    return "\n".join(out)


def extract_tokens(text: str) -> set[str]:
    text = strip_code(text)
    tokens: set[str] = set()
    for pat in TOKEN_PATTERNS:
        tokens.update(m.group(0) for m in pat[1].finditer(text))
    return {
        t for t in tokens
        if len(t) >= MIN_TOKEN_LEN and t not in GENERIC_TOKENS
        and not t.isdigit() and not _is_noise(t)
    }


def load_target(root: Path) -> tuple[str, set[str]]:
    skill = root / "SKILL.md"
    if not skill.is_file():
        raise ValueError(f"missing SKILL.md under {root}")
    text = skill.read_text(encoding="utf-8", errors="replace")
    for extra in sorted(root.rglob("*")):
        if extra.is_file() and extra.suffix in {".py", ".sh"} and "__pycache__" not in extra.parts:
            text += "\n" + extra.name
    return root.name, extract_tokens(text)


def scan_library(lib: Path, exclude: str) -> dict[str, set[str]]:
    peers: dict[str, set[str]] = {}
    for skill_md in sorted(lib.rglob("SKILL.md")):
        if ".archive" in skill_md.parts or "node_modules" in skill_md.parts:
            continue
        name = skill_md.parent.name
        if name == exclude:
            continue
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        scripts_dir = skill_md.parent / "scripts"
        if scripts_dir.is_dir():
            text += "\n" + "\n".join(p.name for p in scripts_dir.iterdir() if p.is_file())
        peers[name] = extract_tokens(text)
    return peers


def grep_hits(tokens: set[str], root: Path, limit_per_file: int = 5) -> dict:
    hits: dict[str, list] = {}
    files = [root / "SKILL.md"] + [
        p for p in sorted(root.rglob("*"))
        if p.is_file() and p.suffix in {".md", ".py", ".sh"} and p.name != "SKILL.md"
        and "__pycache__" not in p.parts
    ]
    low = {t.lower(): t for t in tokens}
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        found = []
        for i, line in enumerate(lines, 1):
            for lt, orig in low.items():
                if lt in line.lower():
                    found.append({"token": orig, "line": i})
                    if len(found) >= limit_per_file:
                        break
            if len(found) >= limit_per_file:
                break
        if found:
            hits[str(f.relative_to(root))] = found
    return hits


def probe(target: Path, lib: Path) -> dict:
    tname, t_tokens = load_target(target)
    peers = scan_library(lib, exclude=tname)
    forward: dict[str, dict] = {}   # peer tokens found inside target files
    reverse: dict[str, list[str]] = {}  # target tokens found inside peer frontmatters
    peer_paths = {p.parent.name: p.parent for p in lib.rglob("SKILL.md")
                  if p.parent.name != tname and ".archive" not in p.parts}
    for peer, ptoks in peers.items():
        inter = t_tokens & ptoks
        if len(inter) >= THRESHOLD:
            reverse[peer] = sorted(inter)
    for peer, pdir in peer_paths.items():
        ptoks = peers.get(peer, set())
        hits = grep_hits(ptoks, target)
        if hits and sum(len(v) for v in hits.values()) >= THRESHOLD:
            forward[peer] = hits
    return {
        "schema_version": 1,
        "target": tname,
        "target_token_count": len(t_tokens),
        "library_peers": len(peers),
        "forward_candidates": forward,
        "reverse_candidates": reverse,
        "threshold": THRESHOLD,
        "scope_note": "counts-only matrix; semantic verdicts belong to the auditor",
    }


def batch(lib: Path) -> dict:
    started = time.time()
    results = {}
    roots = sorted({p.parent for p in lib.rglob("SKILL.md")
                    if ".archive" not in p.parts and "node_modules" not in p.parts})
    for r in roots:
        try:
            results[r.name] = probe(r, lib)
        except ValueError as exc:
            results[r.name] = {"error": str(exc)}
    return {"schema_version": 1, "lib": str(lib), "skills": len(results),
            "elapsed_s": round(time.time() - started, 2), "results": results}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", type=Path, nargs="?", help="target skill root")
    ap.add_argument("--lib", type=Path, default=Path.home() / ".hermes/skills")
    ap.add_argument("--batch", action="store_true", help="probe every skill under --lib")
    ap.add_argument("--json", action="store_true", default=True)
    args = ap.parse_args()
    try:
        result = batch(args.lib) if args.batch else probe(args.target.resolve(), args.lib.resolve())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
