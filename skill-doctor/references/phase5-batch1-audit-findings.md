# Phase5 Batch 1 Semantic Audit Findings

> Audit run: 2026-07-19
> Scope: 11 logical skill units (forks + local-managed) across default, work, work-web, finance profiles
> Auditor: manual (human-in-the-loop)
> Output: `~/.hermes/reports/skill-audit-20260719/phase5-semantic-delta-batch-1-result.json`

## Audit Framework Used

12 semantic dimensions, scored ✅/⚠️/❌, with per-line evidence:

| # | Dimension | Notes |
|---|-----------|-------|
| 1 | 必要性 | Is the skill worth existing? |
| 2 | 正触发 | Clear, verb-driven triggers |
| 3 | 范围边界 | Clear scope |
| 4 | 负触发 | Explicit `When not to use` |
| 5 | 冲突规则 | Precedence with overlapping skills |
| 6 | 所需输入 | Required inputs before execution |
| 7 | 工作流 | Executable steps, not abstract description |
| 8 | 输出格式 | Defined output format |
| 9 | 验证闭环 | Success criteria + verification before claiming done |
| 10 | 可维护性 | Version, author, freshness gate |
| 11 | 风险checklist | Pitfalls / risks |
| 12 | 日志优先 | For system skills: logs first with paths |

Verdict rule: any ❌ = FAIL; any ⚠️ = WARN; all ✅ = PASS.

## Output Schema

```json
{
  "schema_version": 1,
  "batch": 1,
  "input_sha256": "<sha256 of input manifest>",
  "units": [
    {
      "unit_id": "...",
      "path": "/path/to/SKILL.md",
      "verdict": "PASS|WARN|FAIL",
      "dimensions": [
        {"dimension_id": 1, "dimension": "必要性", "status": "✅", "evidence": "path:line summary"},
        ...12 items
      ]
    }
  ],
  "summary": {"unit_count": 11, "verdict_counts": {"PASS": N, "WARN": N, "FAIL": N}}
}
```

## Summary

| Verdict | Count | Units |
|---------|-------|-------|
| PASS | 4 | `ai-providers-config`, `changedetection-monitor`, `cron-management`, `finance-manager` |
| WARN | 6 | `hermes-agent`, `beijing-server-deploy`, `chemical-fiber-quote`, `closeai-usage-tracking`, `color-palette`, `email-drafting` |
| FAIL | 1 | `daily-work-briefing` |

## Key Actionable Findings

### `daily-work-briefing` (FAIL)

- **Missing references**: `references/mail-api.md`, `references/env-and-tokens.md`, `references/crm-api-pitfalls.md` referenced in SKILL.md but do not exist in the package. Canonical equivalents exist in `zoho-mail-crm` skill.
- **Broken script**: `scripts/crm_coql_query.py` calls `get_crm_token.py`, which the SKILL.md itself says does not exist. The skill's documented correct flow uses `~/.hermes/profiles/work/scripts/refresh_zoho_tokens.py` and direct `.env` reads.
- **Missing maintainability metadata**: no version, author, or freshness gate.

### Systematic Gap Across WARN Units

- **日志优先 (logs-first)** was the most common ⚠️. Deployment/server/cron-adjacent skills often omitted explicit log paths or did not make logs the first diagnostic step.
- **可维护性 metadata** (version, author, freshness gate) was missing on several fork-derived and older skills.
- **冲突规则** were implicit or absent on narrow creative skills.

## Remediation Notes

- For missing cross-profile references, prefer canonical skill references (e.g., `zoho-mail-crm/references/env-and-tokens.md`) over broken local references.
- For token refresh, use the verified `refresh_zoho_tokens.py` flow instead of the non-existent `get_crm_token.py`.
- When scoring system skills, enforce dimension 12 (logs-first) strictly; pure creative skills like `email-drafting` can be ✅ with explicit explanation.

## Related References

- [batch-readonly-audit-patterns.md](batch-readonly-audit-patterns.md) — generic 12-dim batch audit template
- [phase5-batch2-calibration-notes.md](phase5-batch2-calibration-notes.md) — later batch calibration
- [library-baseline-audit.md](library-baseline-audit.md) — full-library baseline audit contract
