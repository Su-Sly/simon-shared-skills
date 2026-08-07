# Delegated Skill Remediation Acceptance

Use this protocol whenever subagents audit or rewrite multiple Skills.

## Why this gate exists

A delegated auditor may see a paginated or tool-truncated excerpt and mistake it for the source file. It may then replace a large, valid Skill with a short reconstruction. It may also report `after_warn_count: 0` while its own evidence admits unresolved warnings. Neither result is acceptable evidence.

## Dispatch discipline

1. Keep an immutable package-level snapshot before any worker writes.
2. Give every worker the exact source path plus baseline line count, byte count, and SHA-256.
3. Require paginated reading until `truncated: false`; for large packages also inspect the heading outline and every linked support file relevant to the edit.
4. The first completed worker result is an acceptance calibration. Do not fill the freed concurrency slot until that result passes the checks below.
5. Workers may edit only assigned packages and must return exact changed-file paths.

## Required worker result

For each Skill, require:

- Before and after path, lines, bytes, and SHA-256.
- Concrete before findings mapped to the **fixed 12** Skill Doctor dimensions.
- Exact files changed and content migration map.
- Broken-link and code-fence verification.
- Runtime visibility/readiness evidence.
- After verdict with fail/warn counts consistent with the written findings.
- Cross-cutting checks such as architecture consistency, security-policy evasion and external-system health in separate fields—not invented dimension 13/14 entries.

### Schema lock

Validate both dimension IDs and their semantic names. The accepted set is exactly `1..12`; missing, duplicated, reordered-to-different-meaning, or extra dimensions invalidate the worker verdict. Architecture consistency remains mandatory, but belongs in `architecture_consistency`, not `after_dimensions[13]`.

A result that only says “all PASS” without all 12 after-dimension evidence entries is incomplete. A worker admitting `PARTIAL`, unresolved warnings, missing sections, or unverified content cannot be normalized to PASS by changing counters.

## Parent acceptance checks

A parent auditor must independently:

1. Read the result JSON and compare it to the immutable snapshot.
2. Reject any claim that a source was an ellipsis/placeholder unless raw bytes from the source prove it.
3. If lines or bytes shrink by more than 30%, require proof that removed knowledge is present in `references/` or intentionally obsolete, with a section-level migration map.
4. Re-read the resulting canonical `SKILL.md`; do not accept a worker self-report as completion.
5. Re-run links, fence balance, frontmatter, runtime visibility, and the 12 dimensions.
6. Treat any admitted unresolved defect as a WARN/FAIL. Phrases such as “acceptable”, “does not affect execution”, or “user authorized not to modify” cannot turn an unresolved warning into zero.
7. For safety contradictions—production-server source edits, `docker cp` hotfixes, unsafe config serializers, autonomous Gateway restarts—require an actual fix or keep the Skill failed.

## Reachability and external-state checks

Audit the executable reachability graph, not only files physically inside the Skill package:

- active `SKILL.md`, `references/`, `scripts/`, `templates/`;
- external scripts, cron jobs, config files, cloud objects or services that the Skill explicitly instructs the Agent to run or treats as proof.

If a linked production artifact is unsafe but outside the user's authorization scope, do not silently rewrite it and do not hide it behind a Skill PASS. Record two conclusions: `skill_quality` and `external_system_status`. A truthful, safely gated Skill may pass while live infrastructure remains `BLOCKED/UNREMEDIATED`; overall delivery must still disclose the external blocker.

## Transactional result bookkeeping

1. Inspect the actual queue/result schema before mutation; never assume `pending` or `completed` is a list rather than a count.
2. Build and validate the complete result in memory first: exact unit set, fixed 12 dimensions, non-empty evidence, formula-consistent counters and referenced files.
3. Preserve rejected child output under a clearly named rejected artifact.
4. Write the accepted result, then update queue entries from the authoritative status table and recompute counts.
5. Assert `completed + pending == total == status_count == order_count` before delivery.
6. If a write fails mid-sequence, report the partial side effect and repair from the preserved artifact; never imply the batch update was atomic when it was not.

## Rejection and recovery

- If a worker caused unproven knowledge loss, restore every file it changed from the immutable snapshot before reworking it.
- If only the assessment is invalid and files were unchanged, reject the result without restoring.
- If some edits may be useful, verify those packages individually; never accept an entire batch because one package looks good.
- Record rejected results separately. Do not let them increment completed counts.

## Completion rule

A Skill counts as completed only after independent parent verification returns zero FAIL and zero unresolved WARN, and runtime discovery confirms the intended Profile can load it. Batch completion is the sum of accepted Skills, not submitted worker reports.
