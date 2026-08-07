# Batch Remediation Readback Pattern

Session: batch-002-group-2 (hermes-system-files, hermes-system-upgrade, tdai-management)
Date: 2026-07-20

What this covers: after directly patching a batch of Skills, how to read them back and verify they are still intact before declaring the remediation done.

## When to use

You have just finished Phase 2 direct optimization of multiple Skills and need to be sure the canonical files are still valid before writing the structured result JSON.

## Readback checklist

1. **Re-read the full SKILL.md** (not just the diff). Use `read_file` without offset or with full pagination to guarantee you see the whole file.
2. **Verify frontmatter** — `name` and `description` are present and `description` ≤ 250 characters.
3. **Count code fences** — Markdown fences must be paired. An odd number means an unclosed or stray fence.
   - Quick check: `grep -c '^```' SKILL.md` should be even.
   - If odd, inspect every fence line with line numbers to find the stray one (often a fence after a reference link or a trailing blank line at EOF).
4. **Resolve relative links** — For every `[text](references/...md)` or `` `references/...md` ``, confirm the file exists under the same Skill directory. Use `find` across the Skill tree, not just `linked_files` from `skill_view` (that list can be incomplete for non-Markdown assets).
5. **Verify references you migrated** — If you moved content from SKILL.md to `references/`, confirm the new file was written and the old section was removed or replaced by a pointer.
6. **Record before/after SHA-256** — For each modified SKILL.md, compute `sha256sum` and store it in the structured result JSON. Do not write placeholder values like `"computed_at_write_time"`; replace them with the real hashes after the fact.
7. **Validate the final JSON** — Run `python3 -m json.tool result.json` before finishing.

## Pitfall: odd fence count after reference pointers

A common cause of an odd fence count is adding a reference pointer at the end of a section and leaving a stray fence on the line before EOF, or adding an extra blank line after the last fenced block that gets parsed as an empty fence. When you see an odd count, print every fence line with its line number and walk through the file visually.

## Pitfall: placeholder SHA-256 in structured results

It is easy to generate the JSON first, then compute hashes. If you emit `"computed_at_write_time"` as a placeholder, a later consumer may trust the JSON as canonical and fail to recompute. Always backfill the real SHA-256 values and re-validate the JSON.

## Pitfall: relative link resolution is not transitive

A backtick reference like `` `references/env-safety.md` `` is not a Markdown link; it is just a clue. Before marking it resolvable, search the actual filesystem for that filename under the Skill's own directory. If the Skill references a file from a different Skill, it is not a broken link per se, but it is a dependency you should note in the audit result.

## Related references

- `references/side-effect-free-static-audit.md` — static checks without modifying state
- `references/delegated-remediation-acceptance.md` — why you must re-read files after a sub-agent claims to have fixed them
- `references/full-library-remediation.md` — the full-library remediation workflow
