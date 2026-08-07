# Cross-Profile Edit and Patch-Integrity Pitfalls

Scope: Skill Doctor runs across many Hermes profiles. This reference captures the failure modes seen during 2026-07-20 group-2 remediation so future batches avoid the same tool loops and formatting defects.

## 1. Cross-profile edits require `cross_profile=true`

The `patch` tool has a soft guard that refuses edits to another Hermes profile's `skills/`, `plugins/`, `cron/`, or `memories/` unless you explicitly pass `cross_profile=true`.

What happens if you forget:
- `patch` returns `Cross-profile write blocked by soft guard`.
- If you retry the same call without the flag, you burn tool calls and learn nothing new.
- After several failures, the matching context in the file can drift if the same session produced earlier partial edits, causing the next patch to mismatch even with the correct flag.

Recommendation:
- Before editing a batch, enumerate the canonical paths and note which ones live under a different profile.
- For the very first edit to each cross-profile file, include `cross_profile=true` in the patch call.
- Do not assume that because `read_file` succeeded, `patch` will succeed with the same path; read is read-only, write is guarded.

## 2. Final patches after a loop can introduce formatting defects

When a patch fails multiple times, the agent may have already partially modified the file. The next successful patch can land on a now-different surrounding context, producing artifacts such as duplicate headers, extra blank lines, or orphaned paragraphs.

Example from this session:

Original section header:

```markdown
### 完成验证

不能只看 HTTP 200...
```

After a failed loop and a successful patch, the file became:

```markdown
### 完成验证

### 完成验证
 不能只看 HTTP 200...
```

The duplicate header was introduced because the patch anchor matched the already-modified line, not the original.

Recommendation:
- After any patch that follows two or more failures, immediately re-read the whole file (not just the diff) to check for formatting artifacts.
- Look specifically for duplicate headers, extra blank lines, and broken heading hierarchy.
- If a defect appears, issue a corrective patch with a fresh anchor from the re-read, not from the original plan.

## 3. Danger-gate wording must survive partial patches

When adding destructive-command gates (backup, diff, digital confirmation, rollback), phrase the new section as a self-contained block. If the patch lands in the wrong place because the surrounding section was already partially changed, the gate still reads correctly and is not split across unrelated sections.

Template for a gate section:

```markdown
### 危险/破坏性命令门禁

以下命令在执行前**必须**先输出命令本身，让用户用**数字确认**（如"回复 `1` 执行"）后再执行：

- list the commands

步骤：
1. 明确列出目标路径与影响范围
2. 对覆盖操作给出 `diff`/备份选项说明
3. 等待用户数字确认
4. 执行后展示结果并确认可回滚（如有必要）

禁止自动执行高破坏命令。
```

If this lands at the end of the relevant procedure section rather than mid-paragraph, it remains usable.

## 4. Checklist for batches that touch multiple profiles

Before any cross-profile remediation batch:

- [ ] List every canonical path and its owning profile.
- [ ] Decide whether the Skill is shared (`shared/...`) or profile-specific.
- [ ] For shared Skills, prefer `skills.external_dirs` over physical copies.
- [ ] For the first write to each cross-profile file, use `cross_profile=true`.
- [ ] After each cross-profile edit, re-read the full file to verify formatting and link integrity.
- [ ] After all edits, run a single `find`/`search_files` pass to confirm every markdown link target exists.
