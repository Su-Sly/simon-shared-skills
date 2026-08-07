# Handling Missing SKILL.md Paths in Batch Audits

The manifest `skill_md` path is a snapshot from when the batch was created. Between creation and audit, the skill may have been renamed, moved, archived, or never installed. If `read_file` returns `File not found`:

1. **Do not repeat the same `read_file` call.** That only burns tool budget.
2. **Search the broader skill tree** with `find` or `search_files` for the skill name (not the full path). Example: `find ~/.hermes -path '*/<name>/SKILL.md' -type f`.
3. **If found elsewhere**, record the new path in the unit's evidence and score the unit normally against the discovered file. Also flag `Cross-Profile Drift` if the discovered location differs from the manifest.
4. **If not found anywhere**, mark the unit `FAIL`/`P0` with evidence `"SKILL.md not found at manifest path <path> and no alternate location found via find ~/.hermes"`. Do not let one missing file block the remaining batch.
5. **If the path is in a profile but the canonical is in `shared/`**, score against the canonical and note the profile path as a fork/drift instance.

This prevents the auditor from getting stuck in a read-loop on stale manifests and preserves the integrity of the batch report.
