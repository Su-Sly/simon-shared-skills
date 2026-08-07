# Batch Read-Only Skill Audit — 12-Dimension Framework & Automation

Pattern for auditing N skill units in one pass without modifying any skill file.
Derived from the 2026-07-19 phase3-batch-3 audit of 42 skills across default, work, work-web, and finance profiles.

## When to use this pattern

- User asks for a read-only skill audit across a batch of skills (e.g., `phase3-batch-3.json`).
- Output must be deterministic, reproducible, and verifiable (JSON + Markdown + SHA256).
- The audit must stay read-only: no skill files are patched during the run.

## 12 read-only dimensions

| # | Dimension | What to check |
|---|-------------|---------------|
| 1 | **YAML Frontmatter** | `name` and `description` present; version/author/tags optional but useful. |
| 2 | **Trigger Scope** | Clear `When to Use` / triggers / 触发词; not domain-only. |
| 3 | **Conflict Rules** | `When Not to Use` / conflict rules define boundaries with sibling skills. |
| 4 | **Step-by-Step** | Concrete, ordered workflow with commands or operations, not abstract prose. |
| 5 | **Verification** | Success criteria, checklist, or test command. |
| 6 | **Error Handling** | Common failure modes and fallback/retry/reporting paths. |
| 7 | **Pitfall History** | Past mistakes, traps, or warnings captured for future agents. |
| 8 | **Security Boundary** | Read-only, deletion, or privilege-sensitive rules stated. |
| 9 | **Credential & Secret** | No real keys/tokens/passwords in the skill file; placeholders or env references only. |
| 10 | **External Dependency** | Required tools, packages, services, or environment stated. |
| 11 | **Freshness Gate** | Skill includes a mechanism to re-audit / read-back after persistent changes. |
| 12 | **Cross-Profile Drift** | `fork:` or duplicated units are flagged for diff against upstream/shared versions. |
| 13 | **Completeness** | Covers real user scenarios; not missing critical commands or API endpoints. |

> **Note:** In practice this is often called "12-dimension" but the read-only checklist has 13 rows because `Cross-Profile Drift` and `Completeness` are both essential in a batch audit. Treat the extra row as a session-specific framing, not a contradiction with the general 12-dim quality model in `quality-dimensions.md`.

## Output spec

| File | Format | Required |
|------|--------|----------|
| `<batch>-agent-<n>.json` | Structured JSON with `summary`, `units[]` | Yes |
| `<batch>-agent-<n>.md` | Markdown summary + per-unit details | Yes |
| SHA256 of both files | `sha256sum` or `hashlib.sha256` | Yes |

JSON schema per unit:

```json
{
  "unit_id": "local:name",
  "name": "skill-name",
  "profile": "default/shared",
  "skill_path": "/Users/.../SKILL.md",
  "verdict": "PASS|WARN|FAIL",
  "risk": "P0|P1|P2",
  "dimensions": { "Dimension Name": { "status": "✅|⚠️|❌", "evidence": "..." } },
  "findings": [{ "severity": "P0|P1|P2", "dimension": "...", "path": "...", "line": 0, "evidence": "...", "recommendation": "..." }],
  "strengths": ["..."],
  "phase4": "Next action"
}
```

## Automation template

A Python script is the easiest way to keep a batch audit consistent and fast. Core structure:

1. **Load batch manifest** from the user-supplied JSON file.
2. **Load each `SKILL.md`** by the `skill_md` path in the manifest.
3. **Parse frontmatter** with `yaml.safe_split` or a simple `---` split.
4. **Score each dimension** with regex/heuristics and append human-readable evidence.
5. **Determine verdict and risk** from the dimension statuses.
6. **Write JSON and Markdown**, then print SHA256 hashes.

Key parsing pitfalls captured from the 2026-07-19 run:

- The batch manifest wraps each unit in `{"unit": {...}}`. Do not access `unit['unit_id']` directly; use `unit['unit']['unit_id']`.
- Some frontmatter keys are `description`, some are `desc`; accept both.
- Secret detection must exclude redacted placeholders (`«redacted»`, `***`, `<placeholder>`) and not flag example values.
- `fork:` units are a strong signal of cross-profile drift; score them as ⚠️ by default unless the user has explicitly reviewed the diff.
- If a `SKILL.md` is missing, mark the unit `FAIL`/`P0` and continue; do not abort the whole batch.

## Verdict / risk mapping

| Condition | Verdict | Risk |
|-----------|---------|------|
| Any real secret in skill text | `FAIL` | `P0` |
| Multiple missing dimensions (≥2 ❌) | `FAIL` | `P0` if ≥3 ❌, else `P1` |
| Single missing dimension | `WARN` | `P1` |
| Many ⚠️ (≥5) but no ❌ | `WARN` | `P2` |
| Otherwise | `PASS` | `P2` |

## Typical findings from a large batch

- Most deployment/maintenance skills pass if they already have frontmatter, triggers, steps, and pitfalls.
- The most common `WARN` is a `fork:` unit whose upstream/shared version may have drifted.
- The most common `P0` (if any) is a hard-coded credential that was not redacted.
- **Heuristic over-fitting on "numbered steps"** is a common cause of false FAILs. Many well-written skills describe workflow as hierarchical sections, bullet checklists, or inline commands rather than a flat numbered list. Scoring "Step-by-Step" as ❌ purely because the count of `1. / 2.` lines is < 4 produces false negatives on skills like `frontend-code-review`, `html-file-support-patch`, `gateway-channel-repair`, etc. A better heuristic: count distinct action-bearing headings, imperative bullet blocks, and executable code snippets, and require concrete sequencing rather than a literal numbered list.
- **Missing canonical skill source** causes `SKILL.md` to resolve to a profile-specific path while a shared canonical exists elsewhere (e.g., `inquiry-contact-record` canonical under `profiles/work`, `kanban` canonical under `shared/devops/`). The auditor must map each unit to its effective canonical source and note cross-profile drift, not silently score a forked copy as canonical.

## Batch workflow: re-use, don't duplicate

When running the second (or Nth) batch in the same audit campaign, the natural trap is to write a brand-new script and re-extract everything from scratch. Avoid it.

**Preferred sequence**

1. Look for existing artifacts from earlier batches in the same report directory: `extract_skills.py`, `audit_batch1.py`, `*-extracted.json`, `*-dims.json`.
2. If the extraction script is already correct, **parameterize** it (batch file, output prefix, report paths) and re-run the same script instead of cloning it.
3. If the audit script already implements the dimension logic, **parameterize** it rather than copying it into `audit_batch2.py`, `audit_batch3.py`, etc.
4. If the user-provided batch manifest already includes `static_leads` (pre-computed structural issues), merge them into the final findings as severity `P0`/`P1` instead of recomputing them from the raw text.

**Why this matters**

- Duplicating scripts means later fixes to scoring logic have to be applied in multiple places.
- Re-extracting from scratch can discard useful intermediate metadata (e.g., line numbers, headings, code blocks) that the earlier extraction already normalized.
- A single parameterized script is easier to SHA256-verify and is reproducible across batches.

**Check before writing a new file**

```text
ls /path/to/reports/
grep -l "BATCH_FILE\|OUT_JSON" *.py
```

If a script already contains the dimension logic, patch it to accept `batch_file`, `out_json`, and `out_md` as arguments or top-level constants, then run it for the new batch.

## When to escalate beyond read-only

A read-only audit only records findings. If the user asks to fix the findings, switch to the standard `skill-doctor` modify workflow and patch skills one by one, applying the Freshness Gate after each change.

## Post-run calibration checklist

After the first automated run, always sample the FAIL/WARN units and hand-check at least 3–5:

1. Is the workflow actually missing, or is it expressed in a non-literal format (headings, bullets, embedded commands)?
2. Is the `SKILL.md` path a fork or a canonical source? If a canonical exists elsewhere, the unit should be scored against that canonical and flagged as drift.
3. Are any ❌ dimensions caused by brittle regex (e.g., requiring `Step N` headings, counting only `^\d+\.`) rather than semantic absence?
4. Are verdicts actually FAIL because of real content gaps, or because of over-weighted heuristic rules?

Document the calibration decisions in the run summary and, if needed, update the scoring heuristic before re-running the batch. Do not ship a report where 100% of units are FAIL due to a single over-tuned dimension without noting this as a known calibration issue.
