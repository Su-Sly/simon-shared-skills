# Phase 5 Batch 2 Read-Only Audit Calibration Notes

Session: 2026-07-19 — Phase 5 第 2 批 39 个 Skill 的 12 维只读语义重审。

## What happened

- Input manifest: `/Users/simon/.hermes/reports/skill-audit-20260719/phase5-semantic-batch-2-input.json`
- 39 logical units covering shared/devops, shared/infrastructure, shared/software-development, and work profile skills.
- Automated scoring script: `/Users/simon/audit_batch2.py` (one-off, should be parameterized next time).

## First-run result

- Input SHA256: `11b5f41105e98d836e0f3041a87d82d290aeac2a780535e5686d43097c655e89`
- Output SHA256: `b6d9eb48c486674f8a3e7493dacd59c18212f73bdd1d57ba311d972f02e75d72`
- Verdict counts: PASS 0 / WARN 0 / FAIL 39

## Root cause of the all-FAIL result

The "工作流" (workflow) dimension was scored by a brittle regex that required ≥4 literal numbered/bulleted steps (`^\d+\.\s+` or `-* Step`). Many well-written skills describe workflow through hierarchical headings, imperative bullets, embedded commands, or ordered prose. The script treated these as missing concrete steps and flagged every unit as FAIL.

## Sampled hand-checks

The following skills were read in full and found to have clear, executable workflows despite not meeting the literal step-count heuristic:

| Skill | Why the heuristic failed | Actual workflow structure |
|-------|--------------------------|---------------------------|
| `find-latest-file` | Uses `### 1. 查找最新文件` / `### 2. 确认文件信息` / `### 3. 读取文件内容` | Numbered headings, but regex only counted bullets |
| `frontend-code-review` | Uses `## Review workflow` with embedded bullet steps and numbered focus areas | Bulleted workflow + 5 focus areas, concrete commands |
| `html-file-support-patch` | Workflow is a 5-step ordered list: 查日志→检查现状→单源修复→静态验证→运行时验收 | Markdown list items, not `Step N` |
| `gateway-channel-repair` | 8-step diagnostic flow (`Step 1` through `Step 8`) | Numbered `Step N` headings, but regex was case-sensitive and required bullet/Step prefix |
| `grok-image-to-video` | Workflow is narrative + embedded curl example | Single endpoint workflow with clear input/output steps |

## Additional finding: canonical source mapping

Several units pointed to profile-specific paths while a canonical shared version existed elsewhere:

- `inquiry-contact-record` manifest pointed to `shared/devops/` (no file), canonical is in `profiles/work/skills/inquiry-contact-record/`.
- `kanban` manifest pointed to `shared/autonomous-ai-agents/` (no file), canonical is in `shared/devops/kanban/`.
- The scorer should resolve each unit to its effective canonical source before scoring, then flag cross-profile drift as a distinct warning rather than treating the forked copy as canonical.

## Recommended heuristic fixes

1. **Workflow dimension**: Count distinct action-bearing elements, not literal numbering:
   - Headings that start with a verb or ordinal (`1. 查找`, `Step 1:`, `### 1.`)
   - Imperative bullet blocks under `Workflow`, `步骤`, `流程`, `执行`
   - Code blocks that are part of the execution sequence
   - Return evidence like "found 6 ordered actions under 'Review workflow' at L29"
2. **Canonical resolution**: Before scoring, search all profiles for `SKILL.md` matches and record whether the audited path is canonical, fork, or missing.
3. **Post-run calibration**: When ≥80% of units fail a single dimension, sample 3–5 units and check for heuristic bias. If found, mark the batch as needing recalibration and update the script.

## Status

- The result JSON was written as requested but is currently dominated by false FAILs from the workflow heuristic.
- Next action: recalibrate the scoring heuristic, rerun the batch, and produce a revised result file with corrected verdicts.
