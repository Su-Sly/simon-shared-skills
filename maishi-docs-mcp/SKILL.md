---
name: maishi-docs-mcp
description: "Use when connecting to or using MAISHI Docs through MCP. Safely read or update content with the current employee's permissions; not for maintenance or administration."
version: 1.0.0
author: Simon Su
license: MIT
metadata:
  hermes:
    tags: [maishi-docs, mcp, oauth, knowledge-base, document-management]
    related_skills: [native-mcp]
---

# MAISHI Docs MCP

Use MAISHI Docs as the current employee. The Agent is **not** a separate employee or super-admin: every request is checked against the employee's current Docs access at the moment it runs.

- MCP endpoint: `https://docs.maishimfg.team/mcp`
- Authentication: OAuth 2.1 authorization code flow with S256 PKCE
- Scope: `docs.read docs.write`
- Resource: `https://docs.maishimfg.team/mcp`

A company administrator registers a trusted Agent client once. Each employee then authorizes that client once in the browser; normal use renews automatically. Never ask users to paste passwords, authorization codes, callback URLs, access tokens, refresh tokens, Cookies, or client secrets into chat.

## When to Use

- Connect an already company-approved Agent to MAISHI Docs.
- Find, read, summarize, create, or update Docs content the requesting employee can access.
- Read or edit a Docs-owned structured record using its current version.
- Explain a connection, authorization, permission, conflict, or disconnected-Agent failure in plain language.

## Do Not Use For

- Developing, deploying, debugging, or administering MAISHI Docs.
- Registering an OAuth client, enabling/disabling an Agent client, changing employee/space permissions, or disconnecting somebody else's Agent.
- Direct database, server, SSH, API-key, cookie, or token operations.
- Writing Zoho, OMS, Finance, or another system's authoritative fields through Docs.
- Deleting content: MCP does not provide deletion in this release.

## Connection Workflow

### 1. Establish prerequisites without guessing

Before attempting a connection, determine only these facts from the Agent's protected configuration or official documentation:

- the Agent's real `client_id`, display name, and exact callback URL;
- whether that exact client and callback URL were registered and enabled by the company administrator;
- whether the employee has an active MAISHI Docs account.

Do not invent values from examples or reuse another Agent's identity. Dynamic client registration is intentionally unavailable.

If the Agent supports MCP OAuth discovery, obtain endpoints from MAISHI Docs OAuth metadata and protected-resource metadata. For Hermes, configure the remote server with its approved identity, then run its MCP OAuth login command. Example shape only:

```bash
hermes mcp add maishi-docs --url https://docs.maishimfg.team/mcp --auth oauth
hermes config set mcp_servers.maishi-docs.oauth.client_id '<approved-client-id>' --force
hermes mcp login maishi-docs
```

The `<approved-client-id>` is not a placeholder to guess. It must be the exact client ID already registered by the company administrator.

### 2. Keep consent with the employee

When the browser displays **“允许 Agent 连接”**:

1. show the employee the Agent display name and requested read/write access;
2. tell them to cancel if they did not start this connection;
3. stop and let the employee click **“允许连接”** themselves;
4. never click approval on their behalf or capture the returned callback data.

On success, save credentials only in the Agent's protected credential store, call `whoami`, and reply exactly:

> 麦石文档已连接

If an interactive browser cannot be opened, provide the authorization URL only through the user's local trusted interface; never post one-time URLs or returned callback data into shared chats.

### 3. Verify before claiming success

Connection success requires both:

- OAuth completion reports success; and
- `whoami` returns the intended employee and the intended Agent connection.

If either check fails, report that the connection is not complete and use the failure handling below.

## Safe Use Workflow

Follow this sequence for every request.

1. **Identify the employee** — call `whoami` when the connection starts, reconnects, or the identity may be unclear.
2. **Locate authorized content** — use `list_spaces`, `list_documents`, `get_document`, `list_records`, or `get_record`. Never infer a document code or another person's visibility.
3. **Read the current state before changing it** — retain the returned current version.
4. **Describe a requested write** — state the target document/record and intended change in plain language before a material create or update. Do not ask for confirmation for an explicitly requested, narrow change.
5. **Write safely** — use the appropriate MCP tool; every write uses a unique, stable `request_key`. Updates must carry the just-read `expected_version`.
6. **Verify and report** — read back the changed target where the MCP result does not already include the authoritative new state. Report the document/record, completed action, and any conflict or access refusal.

## Capability Boundaries

| Request | Use | Required safety rule |
|---|---|---|
| Confirm identity | `whoami` | Do this before first use and after a new authorization. |
| Browse content | `list_spaces`, `list_documents`, `get_document` | Return only what the current employee may access. |
| Create a document | `create_document` | Confirm target space and use a unique `request_key`. |
| Change a title or block | `update_document_title`, `update_block` | Read first; provide current `expected_version` and a unique `request_key`. |
| Add a block/source/attachment | `create_block`, `create_source`, `link_source`, upload tools | Do not duplicate a write after an uncertain result; reuse the same request key only for the same request. |
| Change a Docs-owned record field | `set_record_field`, `clear_record_field` | Read first; write only Docs-authoritative fields and supply current `expected_version`. |

## Conflicts and Failures

- **Company has not approved this Agent**: say “公司尚未允许这个 Agent 接入麦石文档，请联系管理员登记这个 Agent。” Do not attempt another client identity.
- **Employee is not active or lacks access**: say what access is missing, without naming other employees or spaces.
- **OAuth login expired, was cancelled, or the connection was disconnected**: ask the employee to start a fresh browser connection. Do not retry a one-time authorization URL or callback.
- **403 permission refusal**: stop. Do not work around it by using a different identity, endpoint, or copied content.
- **409 version conflict**: do not overwrite. Read the latest target, summarize the competing change, and ask the employee whether to keep the current value or apply the proposed value.
- **422 authority conflict**: explain that the field belongs to Zoho, OMS, Finance, or another source system and is read-only in Docs.
- **Network/server failure**: report that completion is unknown. For a write, retry only with the *same* request key and identical payload; otherwise read the target first to determine the result.

## Disconnecting

The employee may open **头像菜单 → 我的 Agent 连接** in MAISHI Docs and choose disconnect. An administrator may also disconnect a connection. Once disconnected, the next MCP request must be refused.

Do not tell users that disconnecting merely pauses access: it revokes the connection and its tokens. Reconnection requires a new employee browser confirmation.

## Completion Checklist

- [ ] The intended employee and Agent identity were verified with `whoami`.
- [ ] No password, token, authorization code, callback data, Cookie, client secret, or sensitive document content was exposed in chat or logs.
- [ ] Every changed target was read at its current version before update.
- [ ] Each write used the right `request_key`; uncertain outcomes were not duplicated.
- [ ] A successful action was confirmed by the MCP response or a read-back.
- [ ] A conflict, refusal, or incomplete operation was reported honestly rather than treated as success.
