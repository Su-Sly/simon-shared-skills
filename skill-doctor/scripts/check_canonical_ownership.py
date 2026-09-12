#!/usr/bin/env python3
"""Check that a named Skill has one physical canonical and expected Profile visibility."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

EXCLUDED = {".git", ".archive", ".venv", "venv", "node_modules", "site-packages", "__pycache__"}
SUPPORT = {"references", "templates", "assets", "scripts"}


def frontmatter_name(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return None
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    try:
        data = yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return None
    value = data.get("name") if isinstance(data, dict) else None
    return str(value).strip() if value else None


def is_active_candidate(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return False
    if any(part in EXCLUDED for part in rel.parts):
        return False
    # A SKILL.md below a support directory of another Skill is archived/reference data.
    current = root
    for part in rel.parts[:-1]:
        if part in SUPPORT and (current / "SKILL.md").is_file():
            return False
        current /= part
    return True


def scan_root(root: Path, skill_name: str) -> set[Path]:
    if not root.is_dir():
        return set()
    matches: set[Path] = set()
    for path in root.rglob("SKILL.md"):
        if is_active_candidate(path, root) and frontmatter_name(path) == skill_name:
            matches.add(path.resolve())
    return matches


def load_external_dirs(config_path: Path) -> list[Path]:
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return []
    values = ((config.get("skills") or {}).get("external_dirs") or []) if isinstance(config, dict) else []
    return [Path(str(value)).expanduser().resolve() for value in values]


def discover_profiles(home: Path) -> list[str]:
    """Return default plus every Profile that has a config.yaml, in stable order."""
    profiles = ["default"]
    profiles_dir = home / "profiles"
    if profiles_dir.is_dir():
        for entry in sorted(profiles_dir.iterdir()):
            if entry.name in EXCLUDED or not entry.is_dir():
                continue
            if (entry / "config.yaml").is_file():
                profiles.append(entry.name)
    return profiles


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill-name", required=True)
    parser.add_argument("--hermes-home", default="~/.hermes")
    parser.add_argument(
        "--profiles",
        default=None,
        help="Comma-separated Profiles; default discovers every Profile with a config.yaml.",
    )
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()

    home = Path(args.hermes_home).expanduser().resolve()
    profiles = (
        [item.strip() for item in args.profiles.split(",") if item.strip()]
        if args.profiles
        else discover_profiles(home)
    )
    roots_by_profile: dict[str, list[Path]] = {}

    for profile in profiles:
        if profile == "default":
            profile_home = home
        else:
            profile_home = home / "profiles" / profile
        local_root = profile_home / "skills"
        roots = [local_root.resolve(), *load_external_dirs(profile_home / "config.yaml")]
        roots_by_profile[profile] = list(dict.fromkeys(roots))

    all_roots = {root for roots in roots_by_profile.values() for root in roots}
    physical_matches = sorted({path for root in all_roots for path in scan_root(root, args.skill_name)})
    visibility = {
        profile: sorted({path for root in roots for path in scan_root(root, args.skill_name)})
        for profile, roots in roots_by_profile.items()
    }

    errors: list[str] = []
    if not physical_matches:
        if not args.allow_missing:
            errors.append("skill_missing")
    elif len(physical_matches) != 1:
        errors.append("multiple_physical_copies")

    if physical_matches:
        for profile, matches in visibility.items():
            if len(matches) != 1:
                errors.append(f"{profile}_visibility_count_{len(matches)}")

    result = {
        "ok": not errors,
        "skill_name": args.skill_name,
        "profiles": profiles,
        "physical_count": len(physical_matches),
        "physical_paths": [str(path) for path in physical_matches],
        "visibility": {profile: [str(path) for path in matches] for profile, matches in visibility.items()},
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
