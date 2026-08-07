# Secret-bearing backup Skill audit

Use this check when a Skill packages `.env`, `auth.json`, tokens, session databases, customer data, or other high-impact secrets into local or cloud backups.

## Evidence layers

Do not collapse these into “backup succeeded”:

1. **Archive construction** — exact inclusion/exclusion list, permissions, consistency method, local hash.
2. **Transport** — TLS and successful upload.
3. **Storage controls** — public ACL, least-privilege credentials, client-side encryption or verified SSE, key custody, versioning/immutability, retention deletion behavior.
4. **Remote integrity** — object HEAD size plus checksum verification. A sidecar existing beside an object is not proof unless its value is actually checked.
5. **Recoverability** — isolated restore drill, path-traversal/link/device-file rejection, database integrity, selective activation and rollback.

Upload success, ETag, object size, or a private Bucket alone does not prove confidential or recoverable backup.

## Skill verdict vs external state

Keep two conclusions:

- `skill_quality`: whether the Skill accurately discovers risk, gates side effects, and defines verification.
- `external_system_status`: whether the live backup system is currently secure and recoverable.

A corrected Skill may pass while the external system remains `BLOCKED` or `UNREMEDIATED`. Do not turn that external risk into zero, and do not fail a truthful refusal-only Skill merely because production remediation needs separate authorization.

## Safe behavior when controls are missing

- State the dated, read-only evidence and its expiry.
- Refuse to describe the backup as secure or disaster-recovery-complete.
- Do not proactively create additional secret-bearing cloud objects.
- Treat changes to encryption, retention, prune/versioning, cron, restore format, or production scripts as separately authorized work.
- Preserve existing artifacts; do not delete or rewrite historical objects during a Skill audit.

## Restore gate

1. Download into a permission-restricted staging directory, never directly over the live home/application path.
2. Verify remote size and checksum.
3. Inspect members before extraction; reject absolute paths, `..`, unsafe links, device files and unexpected owners/modes.
4. Extract to isolated staging and produce a selective restore manifest/diff.
5. Back up the live target and obtain the required numeric confirmation.
6. Activate only the approved subset; coordinate service lifecycle through its governing safety Skill.
7. Validate parsing, database integrity, logs and user-visible function; roll back on failure.

Direct commands such as `tar -x... -C ~` over a live home directory are a P0 restore design failure.