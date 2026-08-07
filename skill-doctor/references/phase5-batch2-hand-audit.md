# Phase 5 Batch 2 人工语义审核结果（第 2 批 10 单元）

Session: 2026-07-19
Input: `/Users/simon/.hermes/reports/skill-audit-20260719/phase5-semantic-delta-batch-2-input.json`
Output: `/Users/simon/.hermes/reports/skill-audit-20260719/phase5-semantic-delta-batch-2-result.json`

## 单元与判定

| unit_id | 路径 | verdict | 主要 ❌/⚠️ |
|---|---|---|---|
| local:hermes-agent-patching | shared/devops/hermes-agent-patching/SKILL.md | WARN | 可维护性：缺少 Skill Freshness Gate / version |
| local:hermes-disk-health | shared/devops/hermes-disk-health/SKILL.md | FAIL | 输出格式：全文无 Output Format 段落；所需输入：无独立 Required Inputs 段落 |
| local:hermes-gateway-management | shared/devops/hermes-gateway-management/SKILL.md | WARN | 可维护性：缺少 Skill Freshness Gate / version |
| local:html-file-support-patch | shared/devops/html-file-support-patch/SKILL.md | PASS | — |
| local:maishi-homepage | profiles/work-web/skills/software-development/maishi-homepage/SKILL.md | WARN | 可维护性：良好；但严格意义上缺少独立 Required Inputs 段落（作为单页静态应用可接受） |
| local:maishi-inventory | shared/software-development/maishi-inventory/SKILL.md | PASS | — |
| local:maishi-oms | shared/software-development/maishi-oms/SKILL.md | PASS | — |
| local:maishi-payroll | profiles/work-web/skills/software-development/maishi-payroll/SKILL.md | WARN | 缺少独立 Required Inputs；缺少显式日志优先排障 |
| local:maishi-quote-track | profiles/work-web/skills/software-development/maishi-quote-track/SKILL.md | WARN | 缺少独立 Required Inputs；缺少显式日志优先排障 |
| local:maishi-tasks | profiles/work-web/skills/software-development/maishi-tasks/SKILL.md | WARN | 缺少独立 Required Inputs（2200+ 行大 Skill 无独立收集段） |

## 值得记录的模式

### 工作流判定不依赖字面编号

`hermes-gateway-management`（L69-143）、`html-file-support-patch`（L36-42）、`maishi-homepage`（L43-55、L69-82）均使用动作性标题、祈使 bullet 或顺序连接词描述清晰工作流，人工判定为 ✅。自动化脚本若只看 `^\d+\.\s+` 会误判。

### 静态单页 Skill 的 Required Inputs 可宽松

`maishi-homepage` 只维护一个单页静态门户，触发范围单一，工作流通过"本地改 → scp → curl 验证"已隐含输入。因此没有独立 Required Inputs 仅作为 ⚠️ 而非 ❌。

### 大型业务系统 Skill 的 Required Inputs 必须独立

`maishi-tasks`（2218 行）、`maishi-payroll`、`maishi-quote-track` 涉及多容器、多模块、数据库、版本号、部署验证。没有独立 Required Inputs/Preflight 段落时，人工判定为 ⚠️——因为大 Skill 需要显式收集操作类型、影响范围、成功场景、回滚方式，否则容易遗漏关键输入。

### 输出格式缺失是硬性 FAIL

`hermes-disk-health` 全文没有 Output Format/输出格式段落，因此无法定义完成时返回给用户的结构。人工判定为 ❌ → FAIL。

### 日志优先指引差异

- `hermes-agent-patching`、`hermes-gateway-management`、`hermes-disk-health`、`html-file-support-patch`、`maishi-inventory`、`maishi-oms`、`maishi-tasks` 均明确将日志/可观测性作为排障或验证第一步。
- `maishi-payroll`、`maishi-quote-track` 只有容器内 grep 版本号和 curl 验证，没有显式"先查日志"的排障指引，判定为 ⚠️。

## 可复用产出

- 审核结果 JSON：`/Users/simon/.hermes/reports/skill-audit-20260719/phase5-semantic-delta-batch-2-result.json`
- 输出 SHA256：`fc93c216686ee9817db0a282a7a20baff9f2df0e297766e4ab4ed43d49b32f43`
- Verdict counts：PASS 3 / WARN 6 / FAIL 1
