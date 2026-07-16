# Systematic Audit Patterns — From 31-Skill Batch Review

Recurring quality gaps found across software-development skills (2026-07-14 audit).
Use these as a quick-check heatmap when auditing similar skills in batch.

## High-Frequency Gaps (by dimension)

### Dimension 12: 日志与可观测性 — 9/31 skills ⚠️

**Symptom:** Skill covers Docker deployment, service restart, or config changes,
but nowhere does it say "排障第一步查日志" with a concrete log path.

**Most affected:** All `maishi-*` deployment skills, `ios-development`,
`finance-ai-center`, `customer-cms`.

**Fix template:**
```
## 排障日志

| 组件 | 日志路径 |
|------|---------|
| 后端容器 | `docker logs <container> --tail 50` |
| Nginx | `grep '<domain>' /var/log/nginx/access.log \| tail -30` |
| 构建 | `docker compose logs --tail 20` |
```

**Rule of thumb:** If the skill triggers on "部署/重启/配置" AND involves Docker,
it MUST list at least one `docker logs` command as the first diagnostic step.

---

### Dimension 10: 简洁性 — 12/31 skills ⚠️

**Three sub-patterns:**

1. **Pitfall creep** — P1...P39+ all inline in SKILL.md. The main file becomes
   a pitfalls encyclopedia. *Seen in: maishi-oms (P1-P39), maishi-inventory
   (P1-P26), ios-development (25+ entries).*

   **Fix:** Keep Top 5 pitfalls in SKILL.md. Move full list to
   `references/pitfalls.md` (which usually already exists but isn't used).

2. **Code block bloat** — Full Python/JS scripts (50+ lines) inline instead of
   in references/. *Seen in: ios-development (JWT generation, ASC API calls),
   simplify-code (3 reviewer prompts).*

   **Fix:** Move code >20 lines to `references/`. SKILL.md keeps the command
   that runs it, not the code itself.

3. **Historical changelog** — "已完成新增功能" / "已清理" lists accumulate.
   *Seen in: finance-ai-center (8+ completed features, 12+ cleaned items).*

   **Fix:** Move to `references/changelog.md`. SKILL.md should describe current
   state, not history.

---

### Dimension 4: 负触发 — 8/31 skills ⚠️/❌

**Symptom:** No "When Not to Use" section. Skill triggers on broad keywords and
collides with sibling skills.

**Most affected:** `xcode-build`, `coding-agents`, `code-review`, all `.archive/`
skills, `flask-dashboard`, `codebase-inspection`.

**Fix:** Every deployment/system skill needs a "When Not to Use" that lists:
- Sibling systems (e.g., "CRM → `maishi-crm`")
- Different scope (e.g., "真机部署 → `ios-development`")
- Simpler alternatives (e.g., "简单单文件修改可直接在 Hermes 中完成")

---

### Dimension 2: 触发正面 — 5/31 skills ⚠️

**Symptom:** Description uses "Tool: feature list" format instead of
"Use when..." with trigger verbs.

**Examples found:**
- `"Inspect codebases w/ pygount: LOC, languages, ratios."` → should be
  `"Use when user asks for LOC count or codebase size metrics."`
- `"Author in-repo SKILL.md: frontmatter, validator, structure."` → should be
  `"Use when creating or editing skills in the hermes-agent repo tree."`

---

## Duplicate Skill Pairs

Three pairs found with >80% content overlap. Background curator should consolidate:

| Pair | Overlap | Recommendation |
|------|---------|----------------|
| `plan` ↔ `writing-plans` | Both write implementation plans to files | Merge into `writing-plans`; `plan` adds nothing unique except "no execution" constraint |
| `flask-dashboard` ↔ `data-dashboard` | Same Flask+SQLite+Chart.js stack | `data-dashboard` is more complete; delete `flask-dashboard` |
| `fullstack-vps-deploy` ↔ `nginx-subdomain-deployment` | SSL+Nginx config is 100% duplicated | Extract SSL config into `fullstack-vps-deploy/references/ssl-setup.md`; delete `nginx-subdomain-deployment` |

---

## Structural Anti-Pattern: Reference Files with SKILL.md Frontmatter

`debugging/references/` contains 4 files (`node-inspect-debugger.md`,
`python-debugpy.md`, `systematic-debugging.md`, `hermes-tui-debugging.md`),
each with full SKILL.md frontmatter (name, description, version, metadata).

**Problem:** They look like standalone skills but `skill_view` can't load them
by name — they're buried in references/. The `debugging` umbrella SKILL.md is
just a 40-line index pointing to them.

**Options:**
1. **Promote** each to a standalone skill in `software-development/` and make
   `debugging` a thin umbrella with cross-references.
2. **Strip frontmatter** from the reference files and make them pure reference
   docs (no `name:`/`description:`/`version:`).
3. **Merge** the 4 references' content into `debugging/SKILL.md` as sections
   (would be ~800 lines — too long, so option 1 or 2 is better).

---

## Quick-Check Heatmap for Batch Audits

When auditing N skills in one pass, score each dimension per skill but only
report ⚠️/❌. Use this to spot systematic patterns:

```
                    Dim 1  2  3  4  5  6  7  8  9  10 11 12
maishi-crm          ✅  ✅  ✅  ✅  ✅  ✅  ✅  ✅  ✅  ✅  ✅  ⚠️
maishi-oms          ✅  ✅  ✅  ✅  ✅  ✅  ✅  ✅  ✅  ⚠️ ✅  ⚠️
maishi-inventory    ✅  ⚠️ ⚠️ ✅  ✅  ✅  ⚠️ ✅  ✅  ⚠️ ✅  ⚠️
...
```

**Pattern detection rules:**
- ≥3 skills with ⚠️ on same dimension → systemic gap, mention in audit summary
- Any dimension with ❌ across multiple skills → highest priority fix
- Duplicate pairs → flag for curator consolidation, don't fix inline
