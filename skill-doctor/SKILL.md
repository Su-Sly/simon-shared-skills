---
name: skill-doctor
description: "Use when user asks to create, review, rewrite, debug, simplify, restructure, or improve another Skill, SKILL.md, agent instruction, workflow prompt, or reusable agent capability. 触发：审一下、审核、改一下这个Skill、看看这个Skill有没有问题、Skill质量、skill-doctor、诊断Skill为什么不触发。"
version: 3.4.18
author: Simon
metadata:
  hermes:
    tags: [skills, optimization, review, architecture]
---

# Skill Doctor

审核、创建、优化 Skill。目标是让一个 Skill 成为**可靠的任务控制模块**——模型能识别、加载、执行，不需猜。

## When to Use

- 审查/诊断/改写/简化/重构现有 Skill
- 创建新 Skill
- Skill 触发不稳定、执行不一致、输出格式混乱
- 诊断 Skill 为什么没被触发
- 解决多个 Skill 间的冲突
- 判断某项任务该用 Skill、memory、模板还是工具

## When Not to Use

- 普通写作、翻译、编码、客服邮件、商务分析
- 只是内容里有"指令"就算 Skill——审查的对象必须是一个 Skill/提示词模块/可复用 Agent 指令

## Conflict Rules

- 与 `hermes-agent-skill-authoring` 冲突时：创建**新** Skill 且需要入库 frontmatter 验证用它；**审核/优化**已有 Skill 用本 Skill
- 与 `coding-agents` 冲突时：本 Skill 只管 Skill 质量，不涉及代码实现

## Required Inputs

审查前拿到：
- Skill 文件内容（SKILL.md 或等价）
- 用户反馈（如有）：触发不稳定？输出格式乱？太长？

缺少上述信息时，直接要，不要猜。

---

## 工作流

### Phase 1: 诊断（先看再改）

按以下 12 维度逐项打分（✅/⚠️/❌），≥3 个 ⚠️ 或任 1 个 ❌ 就要动手改：

| # | 维度 | 检查 |
|---|------|------|
| 1 | **必要性** | 这活值得一个 Skill 吗？还是 memory/模板够用？是否一个 Skill 塞了多个不相关任务？ |
| 2 | **触发正面** | 有没有明确的 `Use this Skill when the user asks to [动词] [任务对象]`？description 是否主要描述**应该执行的目标行为**，而不是靠一串“不要做X”反向塑形？ |
| 3 | **触发覆盖面** | 覆盖的是清晰的**任务类别**还是笼统的**领域**？同一个触发条件会不会命中 3 个不同 Skill？修改路由后是否准备了明确正例、口语正例、相邻负例和冲突例？ |
| 4 | **负触发** | 有没有写 `Do not use when: [...]`？负触发是否只用于真实排除边界，而非代替正向工作流？ |
| 5 | **冲突规则** | 和别的 Skill 撞了怎么办？是否明确优先级、输入差异或路由条件，而不是让模型猜？ |
| 6 | **输入要求** | 执行前需要哪些信息？没说就得猜，猜就出错。 |
| 7 | **工作流** | 有 4-8 步可执行步骤吗？每步能做（具体命令/操作）？还是抽象描述？**注意**：步骤不一定非是 `1. 2. 3.` 编号；动作性标题、有序 bullet、嵌入命令块且能形成清晰顺序也算。评分时不能只看 `^\d+\.\s+` 行数。 |
| 8 | **输出格式** | 返回什么格式？Markdown/纯文本/JSON？要不要解释？格式是否可验证？ |
| 9 | **质量标准与验证闭环** | 先判断验证类型：执行/状态变化用 `execution_verification`，产物质量用 `quality_gate`，纯参考且不产生待验收结果用 `not_applicable`。前两类是否定义了完成标准和可观察证据？执行验证是否要求成功后才能报告完成？不能仅凭是否存在 `Verification` 标题评分。 |
| 10 | **简洁性** | 越短越好。有没有"以防万一"的内容？有没有该进 references/ 却堆在 SKILL.md 里的长代码？**引用数量 >5 个时，检查是否可按使用场景合并。** 格式卫生：frontmatter description ≤250 字符？有无孤立的 ` ``` `（开/闭 fence 不配对）？有无空的 code block（打开后立刻关闭，无内容）？ |
| 11 | **硬规则 vs Checklist** | 高风险操作是否用了 checklist 而非被动规则？判断公式：**不可逆性 × 前置条件复杂度 × 失败后果严重性**。三者乘积高的场景，硬规则不可靠——agent 会在压力/惯性下把"这是修复"重新框定为规避规则的理由。Checklist 把被动知识变成主动验证——agent 到决策点强制自问，不靠回忆。 |
| 12 | **日志与可观测性** | 判断是否适合加日志：**适合** — Skill 涉及服务重启、配置变更、部署、定时任务、API 调用、进程管理中的任一项；**不适合** — 纯文本生成、翻译、格式转换等不涉及系统状态。如果适合——排障第一步是查日志还是直接猜原因？有没有写明日志路径（如 `~/.hermes/logs/gateway.log`、`docker logs <container>`）？评分：✅ 排障第一步查日志 + 有明确路径 / ⚠️ 提到日志但没路径或不是第一步 / ❌ 适合加日志但完全没提 |

**诊断报告质量标准**：每个维度评分必须附具体证据——引用 Skill 原文行号或内容片段，不能只打 ✅ 不说为什么。

**输出诊断时**：≤200 行的 Skill 用 bullet 摘要，>200 行用 table 格式。

**行为路由验收（修改触发时强制）**：修改 description、When to Use、When Not to Use 或冲突规则时，不能只做YAML和文案检查。至少准备明确正例、口语正例、相邻负例、冲突例和加载后执行例；用户报告过误触发、修改description、新增/重命名Skill或存在明显重叠时，必须在新会话/隔离会话做真实调用抽样。当前会话已预加载Skill不能证明自动路由成功。未做真实调用时只能报告“静态结构通过”，不得声称触发准确率已验证。完整方法见 [references/behavioral-routing-audit.md](references/behavioral-routing-audit.md)。

**指令覆盖检查**：优先写模型应该执行的目标动作；`Do not` 只保留给安全边界和真实排除条件。检查Skill未说明的决策是否会被模型先验擅自补全，并将每个空白归为“补齐、明确分支、刻意开放”，避免一边遗漏关键合同、一边为填空把Skill写成百科。

**批量审计模式**：一次审 N 个 Skill 时，只输出有问题的维度（⚠️/❌），跳过全 ✅ 的 Skill。审完后汇总高频问题维度——如果 ≥3 个 Skill 在同一维度 ⚠️，这是系统性缺口而非个别问题，在审计总结中单独提出。派发子 Agent时必须固定原始12维、JSON schema、verdict公式和risk/verdict分离规则；主 Agent按输入集合、维度顺序、证据、hash与公式重新验收，不采用子 Agent自报统计。异步任务状态显示 `completed` 也必须检查产物文件存在、子 Agent是否自述未完成、证据是否只是启发式套话。Phase 5允许对逐文件SHA完全一致且旧基线有效的单元继承语义结果，只重审变化/新增单元；必须记录继承数与重审数，不能冒充全量人工重读。最终人读报告必须把内容质量 verdict 与运行影响 tier 分开，并明确严格 FAIL 不等于运行故障。详见 [references/batch-audit-patterns.md](references/batch-audit-patterns.md) 的高频问题热力图和重复 Skill 检测矩阵，以及 [references/library-baseline-audit.md](references/library-baseline-audit.md) 的统一批次输出合同与 Human-facing report gate。

**批量审计后校准**：自动化评分经常把实际合格的 Skill 判为 ❌（尤其是“工作流”维度过度依赖 `^\d+\.\s+` 编号）。每次批量运行后，必须从 FAIL/WARN 中随机抽样 3–5 个做人工复核。若发现某维度启发式导致系统性误判，在最终报告中明确标注为“校准问题”，并更新评分启发式后重新跑该批。具体案例见 [references/batch-readonly-audit-patterns.md](references/batch-readonly-audit-patterns.md) 和 [references/phase5-batch2-calibration-notes.md](references/phase5-batch2-calibration-notes.md)。

**审计完成与治理完成门禁（强制）**：
- `审计完成`只表示范围、证据和报告已生成；允许存在 FAIL/WARN。
- `治理/整改完成`要求已授权范围内的 FAIL 全部修复并逐项重审通过；未被用户明确接受的 WARN 也必须列为未完成项。
- 只要报告仍有严格 FAIL，就不得回答“整个任务全部完成”“全库已通过”或把条件通过简写为通过。用户问“都完成了吗”时，必须先回答“未全部完成”，再分别列审计执行、运行完整性、内容治理状态。
- 批量整改不能只信子 Agent 的“已修改”；必须对最终 canonical 路径重新运行 Skill Doctor并回读。共享根迁移后必须再次验收，旧副本上的通过结论不得继承。

**架构一致性语义检查（强制）**：应用维护 Skill 必须检查其操作路径是否自相矛盾：代码权威源、本地 Git→远端→服务器部署链路，与服务器直改、SCP/`docker cp`热补丁、生产服务器打 tag 是否冲突；数据库命令中的 `--accept-data-loss`、reset/drop/force 等破坏性参数是否有备份、diff、数字确认和回滚门禁。此类冲突不能因“有 checklist”就给维度 11 ✅。

**可执行生产示例门禁（强制）**：部署/服务器Skill中的Shell围栏必须逐块通过`bash -n`；可执行围栏不得使用会被Shell解析成重定向的`<app>/<domain>/<port>`占位符，改用环境变量、缺值即停和`set -euo pipefail`。检查授权时序：备份创建、证书请求、Git状态变更、安装、构建、重启和API/数据库写入都必须在Simon下一条消息严格等于数字`1`之后。`git cat-file`只证明本地对象存在，生产部署还要验证目标SHA来自权威远端分支。外部SSH前提缺失时可判Skill质量PASS，但必须单列`production_runtime_verified=false`，不能冒充生产验证。详见 [references/executable-production-example-audit.md](references/executable-production-example-audit.md)。

**安全策略规避门禁（强制）**：Skill若教Agent在某工具/CLI被安全拦截后改用`execute_code`、subprocess、cron、watchdog、脚本、宽泛kill或其他Profile绕过，直接判P0 FAIL；“会断连/当前进程会被杀”不是绕过理由。审核范围必须包含活动`references/`、`scripts/`和`templates/`，不能只修主入口后把可执行旁路留在附件；还要沿主入口的明确调用关系检查包外生产脚本、cron、配置、云对象或服务证据。包外运行物不在本轮授权范围时不得静默修改，但必须把`skill_quality`与`external_system_status`分开：Skill可因如实阻断和正确门禁而PASS，外部系统仍应标`BLOCKED/UNREMEDIATED`并在整体交付中披露。正确修复是停止、报告拦截原因、转交经授权的外部入口，并验证无授权/被拦截场景都会停止。详见 [references/safety-policy-evasion-audit.md](references/safety-policy-evasion-audit.md)、[references/delegated-remediation-acceptance.md](references/delegated-remediation-acceptance.md) 和 [references/secret-bearing-backup-audit.md](references/secret-bearing-backup-audit.md)。

**官方文档锚定门禁（强制）**：凡 Skill 涉及的对象背后**有“会发布并维护文档的权威方”**，该对象就存在官方文档，Skill 必须锚定官方文档链接并遵循其当前格式，禁止凭记忆写死格式/端点/参数。判断原则（第一性原理）：**官方文档存在的本质 = 权威方定义了对外契约，且契约会演化**。所以判断“什么情况下会有官方文档”，只看一句：这个对象背后有没有会更新文档的权威方？
- **有权威方 → 必有官方文档，必须锚定**：外部平台/SaaS/云服务（企业微信、飞书、Telegram、腾讯云、GitHub、Zoho、Notion——如企业微信推送格式必须遵循企业微信官方格式）、开源项目/工具（Docker、PostgreSQL、ffmpeg、mihomo、FastAPI）、协议/标准（OAuth 2.0、OpenID Connect、MCP、Webhook）、OS/平台能力（macOS launchd、iOS TestFlight、systemd）、Hermes Agent 自身（工具、配置、CLI）。
- **无权威方 → 无官方文档，不硬塞**：自建系统内部逻辑（麦石内部系统、TDAI、自家脚本）、纯本地方案/个人流程（目录约定、个人偏好、一次性操作）。
- 判据是“有没有权威方”，不是内外：自建系统若公开成项目也有官方文档；本地 CLI（如 `launchctl`）反而受 Apple 官方文档管辖。
- **文档会更新**：锚定处必须记录**查证日期**（如 `docs 核对 2026-08-08`）；审计时抽查链接有效性（curl/web_extract）与关键契约是否仍与当前官方文档一致，失效/漂移判 ⚠️。格式以官方最新版为准，不依赖模型记忆里的旧版格式。

**证据分类门禁（强制）**：正则、安全扫描、CLI列表和字符串计数的命中都只是线索。凭据命中必须先排除低熵占位符；运行时列表必须排除终端宽度截断；结构补丁必须限定目标语义块计数；局部修复使用不可变全库基线 + remediation overlay，不能冒充全库重算。详见 [references/audit-evidence-classification.md](references/audit-evidence-classification.md)。Markdown 链接分层、inline-code 跨行误扫、物理文件 hash 继承和语义合同锁定见 [references/markdown-static-audit-pitfalls.md](references/markdown-static-audit-pitfalls.md)。

**运行时名称解析门禁（强制）**：逻辑unit去重可能掩盖多个活动物理副本；`hermes skills list`显示enabled只证明可见性，不证明裸名称能唯一解析。全库治理必须按frontmatter `name`递归扫描default/shared/所有Profile/`external_dirs`，对同名组记录路径、hash和来源分类，并在目标Profile实际用裸名称加载。出现ambiguous时，单一流程保留canonical，其余旧副本优先可逆归档到活动发现范围外；不经用户确认不删除。归档后必须验证旧活动路径消失、归档存在、裸名称唯一加载、各Profile预期可见。详见 [references/runtime-name-resolution-gate.md](references/runtime-name-resolution-gate.md)。

- **分页读取与内容保全门禁**：`read_file` 返回的 `truncated: true`、`hint: Use offset=...` 或工具展示中的 `...` 只表示**本次输出分页/截断**，绝不表示源文件是占位符或内容损坏。重写前必须记录源文件真实行数、字节数和 SHA-256，并分页读完整文件或先建立章节/引用清单。若修改后主文件行数或字节数减少超过 30%，必须同时提供：删改章节映射、迁移到 `references/` 的目标路径、引用存在性验证和知识未丢失证据；缺任一项就拒绝该修改并从快照回滚。批量结果必须记录 before/after 的行数、字节数和 SHA-256，不能只写“已回读”。
- **委派整改验收门禁**：子 Agent 的“PASS”只是待验收自报。父审计必须独立核对快照差异、全文回读、链接/围栏、运行时可见性和12维结论；结果文字仍承认缺章节、格式错误、安全冲突或“可接受警告”时，`after_warn_count` 不得写0。首个返回结果先做校准验收，通过前不补满并发位。若仅评估失真而文件未改，只拒收结果；若发生无证据的大幅删减，恢复该worker改过的全部文件；不能因一个包看起来正确就整批接收。详见 [references/delegated-remediation-acceptance.md](references/delegated-remediation-acceptance.md)。
- **相对路径证据分级**：真实 Markdown 链接 `[x](references/a.md)` 可按当前包解析，不存在即硬错误；反引号中的 `references/a.md`、`scripts/x.py` 只是线索，因为它可能指向相邻 Skill 或目标项目。必须先读上下文，识别是否写明其他 Skill/仓库，再搜索真实目标；不能把所有反引号路径机械升级为 broken reference。`skill_view` 的 `linked_files` 也不是完整文件清单（非 Markdown 资产可能不展示），缺失结论需用实际文件搜索复核。
- **安全修补不能破坏协议常量**：密钥扫描只遮蔽凭据值，不得把 `Authorization: Zoho-oauthtoken`、`Bearer` 等协议 scheme 替换成 `***`。改到可执行脚本后，用假 token + monkeypatch/no-network fixture 验证最终 header 和响应解析，再报告修复。
- **批次 schema 必须校验维度语义映射**：不仅检查维度 ID 为 1–12，还要逐项验证 `dimension_id → dimension` 与本 Skill 原始12维完全一致。固定维度集合必须**恰好**为1–12；缺失、重复或擅自增加第13/14维都拒收。架构一致性、安全策略规避、外部系统状态是强制横切检查，但必须写入独立字段，不能伪装成额外维度。尤其第10维必须是“简洁性”，不能漂移成“可维护性/版本/freshness”。发现命名或判据漂移时，拒收该维度并由主 Agent 按原定义重评；不能只改显示名称后沿用错误分数。

**异步审核完成屏障（强制）**：若批量审核交给后台子 Agent，所有批次完成并由主 Agent读取、复核前，不得声称“12 维全部通过”，也不得把静态 YAML/fence/引用检查冒充语义审核。后台结果尚未返回时，只能标记“语义审核待完成”。子 Agent 结论是线索，不是事实；主 Agent必须区分真实缺陷、误判和既有结构债后再修改。

**批量治理规则铺设**：给一类 Skill 统一加入门禁、验证或安全规则时，范围发现必须先做全 Profile 正向扫描，再做中英文职责关键词的反向漏项扫描。逐项区分具体应用、应用维护 umbrella、通用方法、纯数据操作和官方/归档副本；反向扫描完成前不得宣称范围锁定。补漏后必须从零重跑全量验证，不能沿用补漏前的通过结论。详见 [references/bulk-governance-rollout.md](references/bulk-governance-rollout.md)。

**统一门禁设计要求**：给多个 Skill 加同一完成门禁时，模板必须同时定义：触发事件、执行责任、持久变化判断、跨 Profile 回读方法、交付证据和终止条件。门禁过程中产生的 Skill 文档修改不得重新触发同一门禁；重审只循环到“本次新增问题为 0”，既有非阻塞警告记录但不制造无限循环。最终合并按“不可变旧基线 → changed/new批次 → 定向重评分 → 修复后overlay”排序，并逐变化单元核算 improved/same/regressed/new；验收拆分 audit execution、runtime integrity、content quality 和 overall，存在严格内容债时只能条件通过。详见 [references/library-baseline-audit.md](references/library-baseline-audit.md)。

### Phase 2: 修改（拿到确认再动手）

**默认必须等用户确认诊断后再改**。用户可回复以下任一方式授权：
- 回复 `直接改` 或 `1` → 立即进入 Phase 2 修改
- 回复 `2` 或 `不改` → 放弃本轮审核，不再修改

**全库授权例外**：用户明确说“所有自建 Skill 都审核并优化”“全部直接改”时，该授权覆盖锁定范围内的全部 Phase 2 修改；不得再按 Skill/批次重复确认，也不要把内部并发批次包装成对用户的多个 Phase。建立连续队列并自动排空，完整流程见 [references/full-library-remediation.md](references/full-library-remediation.md)。但用户之后明确要求“完成当前Skill后停止”或表示余额不足时，该新指令立即覆盖自动排空：只验收并入账当前一个逻辑单元，不启动下一单元；自动standing-goal/续跑提示不构成恢复授权，只有用户本人新的明确恢复指令才继续。

**确认 UX**：Phase 1 诊断输出末尾，直接给出数字选项，例如：
```
是否直接改？
1. 直接改
2. 不改，放弃本轮审核
```
不要写成自然语言"你回复 1 我改，回复 2 我放弃"。

修改优先级：
1. **先修触发** — 补正面 + 负触发 + 冲突规则，这是可靠性根基
2. **再补工作流** — 把抽象描述变成可执行的 4-8 步，每步带具体命令/操作
3. **定义输出** — 明确格式、语言、是否带解释
4. **加验证闭环** — 见下方 Verification Pattern
5. **精简长度** — 纯文本说明 → 保留，长代码/示例 → 移到 references/，模板 → 移到 templates/

**改完后自验 checklist（逐项确认后才能交付）：**

```
□ 我改了哪些文件？逐个列出
□ 改完后用 skill_view 回读确认内容正确写入
□ Verification Pattern 的 5 元素是否覆盖（如适用）
□ references 引用的文件都实际存在吗？用 skill_view(name, file_path) 逐个验证
□ 改完后重新加载完整 SKILL.md，整体通读一遍
□ 记录 before/after 行数、字节数和 SHA-256（尤其是行数/字节减少 >10% 时）
□ 对跨 Profile Skill 按实际部署 profile 运行 hermes -p <profile> skills list --enabled-only 确认运行时可见
□ 若产出结构化结果文件，写入 ~/.hermes/reports/skill-doctor-full-remediation-YYYYMMDD/ 并包含 after_fail_count、after_warn_count、verification_evidence
```

任一 ☐ 未确认 → 不报告完成。

### Verification Pattern

先判断验证适用类型，仍沿用 ✅/⚠️/❌，不新增第 13 维或 `N/A` 状态：

| 类型 | 适用场景 | 要求 |
|------|----------|------|
| `execution_verification` | 执行、修改、创建、删除、部署、配置变化、外部状态或事实性结果 | 必须覆盖下方 5 元素；验证失败不得报告完成 |
| `quality_gate` | 写作、翻译、设计、格式转换等产物 | 定义输出标准或质量 checklist；不强制伪造外部状态验证 |
| `not_applicable` | 纯参考知识，不产生需要验收的结果 | 可不设独立验证步骤，但评分证据必须说明不适用原因 |

评分：适用且完整，或不适用且理由成立 → ✅；有验证意图但对象、方法或标准不完整 → ⚠️；明确需要验证却缺失，或失败后仍允许声明完成 → ❌。

对于 `execution_verification`，审核时检查是否包含完整验证闭环：

| 元素 | 检查 |
|------|------|
| **Action** | 做了什么改变？ |
| **Verification Target** | 验证什么对象？ |
| **Verification Method** | 使用什么方法验证？（curl / docker logs / 读页面 / 查数据） |
| **Success Criteria** | 什么结果代表成功？（HTTP 200 / 无 ERROR / 数据一致） |
| **Completion Rule** | 未通过验证时，不得声明完成 |

**差**：
```
Restart the service.
Confirm it works.
```

**好**：
```
Restart the service.

Verify:
- docker ps → container Up
- curl http://127.0.0.1:8080/health → HTTP 200
- docker logs --tail 5 → no ERROR

Only report completion after all checks pass.
```

### Phase 3: 验证（7 问）

1. 模型能判断何时加载吗？
2. 模型能判断何时**不**加载吗？
3. 模型能不猜就能执行吗？
4. 输出格式可预测吗？
5. 够短吗？（能少一行就少一行）
6. 和同类 Skill 冲突了吗？
7. 如果涉及外部状态变化或高影响输出：完成是否有可观察证据？验证方法是什么？验证失败时是否阻止报告完成？

任一回答"否"，回到 Phase 2。

### Phase 3B: 自身修改验证（必做）

改完 Skill 后，用同一套 7 问检查**自己的修改**，不只是被审 Skill：

1. 我改的文件都写入成功了吗？（`skill_view` 回读确认）
2. 我引用的 references 文件都存在吗？（`skill_view(name, file_path)` 逐个验证）
3. Verification Pattern 的 5 元素是否覆盖？（仅 `execution_verification` 强制；其他类型按适用要求检查）
4. 改完后整体通读了吗？（不只看 diff，看全文）
5. 跨 Profile Skill 的拓扑正确吗？先区分“单一共享源”和“独立分叉”。共享源优先用官方 `skills.external_dirs`，并逐个运行 `hermes -p <profile> config check` 与 `hermes -p <profile> skills list`；不能假设子 Profile 自动继承 default，也不能只看文件系统就宣布完成。

---

## 输出格式

**诊断（Phase 1）**：

- ≤200 行的 Skill → bullet format：
```
#### 诊断
* 主要问题: ...
* 触发: ...
* 工作流: ...
* 输出格式: ...
* 冲突风险: ...
* 长度: ...

#### 建议改动
1. ...
2. ...
```

- >200 行的 Skill → table format：
```
| 维度 | 评分 | 证据 |
|------|:--:|------|
| 必要性 | ✅/⚠️/❌ | 引用原文行号或片段 |
| 触发正面 | ✅/⚠️/❌ | ... |
| ... | ... | ... |
```

**修改（Phase 2）**：直接给出改写后的完整 SKILL.md。

---

## Skill 反模式速查

| 反模式 | 症状 | 修复 |
|--------|------|------|
| **百科式** | >300 行、塞 IP/密码/API key、无 When to Use | 拆成 3-5 个 <100 行 Skill，敏感信息移到 references/。详见 [references/slimming-workflow.md](references/slimming-workflow.md) |
| **无触发** | 有内容但无 When to Use，description 是"用于系统维护" | 加动词式触发：\"Use when user asks to deploy/restart/config X\" |
| **流水账** | 20 步工作流、每步一行、没有分支 | 压缩到 4-8 步，抽象模式而非穷举 |
| **猜谜式** | 要求输出"专业"但没定义什么叫专业 | 给具体的格式模板和验证标准 |
| **教AI已知事** | Skill 里塞满 Claude/Hermes 默认就会的通用知识 | 只写偏离默认行为的信息：内部系统边界、命名惯例、已知坑。问：\"AI 不懂这件事的唯一原因是什么？\"写入那个答案 |
| **官方/归档边界误判** | 把 `.archived` 目录或官方 optional 副本当成 canonical 源迁移 | 先确认 `~/.hermes/hermes-agent/skills/` 和 `optional-skills/` 的官方版本；归档目录不是 canonical，迁移前须走 `hermes skills diff/reset/update` 而不是直接 external_dirs |
| **硬规则的幻觉** | "永远不做X"写在 SOUL 里但 agent 仍然违规 | 高风险操作改用 checklist。详见 [references/anthropic-patterns.md](references/anthropic-patterns.md) |
| 过度限定 | 指令太死，不给模型适应具体场景的空间 | 给信息（what），给灵活性（how）。\"你需要 X 数据\"而非\"你必须用 curl 调 Y API\" |
| 描述范围漂移 | description 未覆盖正文中实际涉及的技术/模式（如正文含 Docker 但 description 只写 Nginx/SSL/systemd） | 改 frontmatter 时同步更新 description，确保动词 + 对象覆盖 SKILL.md 实际范围 |
| 双语重复章节 | 同一章节同时出现英文和中文版本（如 Output Format 重复） | 保留一种语言，删除重复；确保更新时只改一处，避免两个版本不同步 |
| **官方文档缺失/凭记忆** | 涉及外部平台/开源工具/协议/OS能力（有权威方的对象）却无官方文档链接，格式/端点/参数凭模型记忆写死 | 锚定官方文档链接 + 查证日期；格式遵循官方最新版（见官方文档锚定门禁） |


---

## References（按需加载）

- **Hermes Agent 官方文档**（docs 核对 2026-08-08）：https://hermes-agent.nousresearch.com/docs — 本 Skill 引用的 Hermes CLI 命令（`hermes skills`、`hermes -p <profile> config check`、`hermes skills diff/reset/update` 等）以官方文档最新版为准；CLI 命令语义或参数变化时先查此文档再写死进任何 Skill。
- [references/v3.4.0-verification-pattern.md](references/v3.4.0-verification-pattern.md) — v3.4.0 速查：Verification Pattern 5 元素 + 批量审计流程 + 跨 profile pitfalls
- [references/slimming-workflow.md](references/slimming-workflow.md) — 瘦身工作流：>300 行 Skill 的 5 步拆分流程 + 实战案例 + **跨 Profile 瘦身陷阱**（skill_manage 无法跨 profile patch，必须用 patch/write_file 工具 + cross_profile=True）
- [references/anthropic-patterns.md](references/anthropic-patterns.md) — Anthropic Skill 实践：Gotchas、Description 写法、渐进式披露、Checklist 决策框架
- [references/cross-profile-sync.md](references/cross-profile-sync.md) — 跨 Profile Skill 拓扑：全库物理+运行时审计、包级哈希、官方 seed 边界、`skills.external_dirs` 单一共享源、迁移顺序与逐 Profile 验证
- [references/quality-dimensions.md](references/quality-dimensions.md) — 质量维度详细说明
- [references/behavioral-routing-audit.md](references/behavioral-routing-audit.md) — 行为路由与指令覆盖：正向引导、负空间分类、正例/负例/冲突例和真实调用验收
- [references/batch-audit-patterns.md](references/batch-audit-patterns.md) — 批量审计模式：高频问题热力图、重复 Skill 检测矩阵、结构性反模式（31-Skill 批量审计总结）
- [references/batch-readonly-audit-patterns.md](references/batch-readonly-audit-patterns.md) — 批量只读 12/13 维审计：输出格式、自动化模板、常见结论与风险映射（42-Skill 2026-07-19 实践）
- [references/batch-missing-path-handling.md](references/batch-missing-path-handling.md) — 批量审计中 manifest `skill_md` 路径不存在时的处理模式：不重复读、先搜索、再标记 FAIL/P0
- [references/phase5-batch1-audit-findings.md](references/phase5-batch1-audit-findings.md) — Phase 5 batch 1 人工语义审核实录：11 单元、12 维、输出 schema 与关键 FAIL/WARN 模式
- [references/phase5-batch2-hand-audit.md](references/phase5-batch2-hand-audit.md) — Phase 5 第 2 批 10 单元人工语义审核结果与模式：工作流判定、Required Inputs 松紧、输出格式缺失 FAIL、日志优先指引差异
- [references/phase5-batch2-calibration-notes.md](references/phase5-batch2-calibration-notes.md) — Phase 5 batch 2 校准实录：工作流维度编号步骤启发式导致 39/39 误判的抽样复核与修复建议；**注意**：已有人工语义审核批次（第 2 批 10 单元）产出，结果以真实路径与状态为准，避免把历史全 FAIL 结论当作当前结论。
- [references/audit-returned-report-gate.md](references/audit-returned-report-gate.md) — 返工场景：已有审计报告被标记 invalid 时，只读重审、替换报告、schema 对齐与自验证流程
- [references/bulk-governance-rollout.md](references/bulk-governance-rollout.md) — 批量治理规则铺设：全 Profile 双向盘点、职责分类、反向漏项扫描、补漏后从零验证
- `references/library-baseline-audit.md` — 全库基线审计：来源分层、logical audit units、异步完成屏障、统一门禁、Phase 5范围漂移、孤立敏感文件与分批回归
- `references/batch-002-group-3-lessons.md` — 批量审核-优化-回读-结构化结果实战手记：Profile 级运行时可见性、before/after 量化指标、references 存在性验证、结果文件标准路径
- [references/audit-evidence-classification.md](references/audit-evidence-classification.md) — 审计证据分类：低熵凭据占位符、CLI截断假阴性、语义块计数、Git边界与增量基线
- [references/runtime-name-resolution-gate.md](references/runtime-name-resolution-gate.md) — 运行时同名解析门禁：物理副本扫描、裸名称唯一加载、可逆归档与跨Profile回归
- [references/safety-policy-evasion-audit.md](references/safety-policy-evasion-audit.md) — 安全策略规避审计：识别换工具/子进程/脚本绕过，覆盖references/scripts并验证拒绝路径
- [references/secret-bearing-backup-audit.md](references/secret-bearing-backup-audit.md) — 含secret备份Skill审计：传输/存储/远端完整性/隔离恢复证据分层，以及Skill质量与外部系统状态双结论
- [references/side-effect-free-static-audit.md](references/side-effect-free-static-audit.md) — 无副作用静态检查：内存编译Python、审计前后文件门禁、缓存副产物清理与manifest重建
- [references/phase5-batch3-manual-audit-gate.md](references/phase5-batch3-manual-audit-gate.md) — Phase 5 Batch 3 手工语义审核门禁：JSON 输出格式、verdict 公式、summary 计数同步与校验脚本
- [references/full-library-remediation.md](references/full-library-remediation.md) — 全部自建 Skill 连续审核优化：运行时 local 范围、宽终端防截断、canonical 去重、行数均衡并发、快照与最终完成门禁
- [references/batch-remediation-readback-pattern.md](references/batch-remediation-readback-pattern.md) — what to verify after directly patching a batch of Skills before writing the structured result JSON

---

## 实战踩坑

| 踩坑 | 后果 | 预防 |
|------|------|------|
| **删副本前没验证共享加载** | 子 Profile 不自动继承 default；删除后 Skill 在运行时不可见 | 先配置 `skills.external_dirs`，逐 Profile 跑 `config check` + `skills list`，验证后再删；详见 `references/cross-profile-sync.md` |
| **只搜 default profile** | 漏掉其他 profile 下的 skill，重复创建已存在的 | `find ~/.hermes -path '*/skills/*/SKILL.md'` 搜全 profile |
| **典型误判 1：工作流维度只看字面 `^\d+\.\s+` 编号。** 许多技能通过动作性标题、祈使 bullet、顺序连接词或嵌入命令块描述工作流。例如 `hermes-gateway-management`（L69-143 用标题和命令矩阵）、`html-file-support-patch`（L36-42 用 `→` 连接的动作 bullet）、`maishi-homepage`（L43-55 用祈使 bullet）。按编号步骤启发式会把这些全部判为 ❌。正确做法：识别动作性标题、命令块、顺序关系，并输出结构证据（如 `Step 1: 查日志` 对应第 38 行）。当某维度高比例 FAIL（≥80%）时，优先抽样复核启发式是否过严。 |
- 在 Phase 1 评分时结合上下文判断；批量脚本设计见 `references/batch-readonly-audit-patterns.md`。
- **跨 Profile 编辑和 patch 完整性陷阱**：批量治理常常涉及编辑多个 Hermes profile 下的 Skill。`patch` 工具对非当前 profile 的 `skills/` 写操作需要 `cross_profile=true`；连续失败后，最后一次成功 patch 可能因上下文漂移而引入重复标题、空行或孤立段落。每次跨 profile 修改后必须完整回读文件，并检查格式卫生。详见 [references/cross-profile-edit-and-patch-integrity-pitfalls.md](references/cross-profile-edit-and-patch-integrity-pitfalls.md)。
| **典型误判 1.1：人工审核时无独立 Required Inputs 段落即判 ⚠️，但对纯静态/单页应用 Skill 可能过严。** 如果 Skill 的范围是单一明确目标（如只维护一个静态首页），并且工作流本身通过部署命令隐含了输入（改哪些文件、改后如何验证），可以维持 ✅，仅在可维护性维度要求补 Freshness Gate。 |
| 见 `references/phase5-batch2-calibration-notes.md` 的人工批次复核记录。 |
| **典型误判 3：把脚本产物 SHA256 自报当验收。** 子 Agent 可能输出 `✅ 所有单元 PASS` 而维度证据为空。主 Agent 必须逐项机器校验：unit_id 集合、维度数量与名称、evidence 非空、verdict 按公式重算。 | 见 `references/library-baseline-audit.md` 第 7 节。 |
| **批量审计中重复读取不存在的 manifest 路径。** 输入清单里的 `skill_md` 路径可能已删除、迁移或从未存在。如果 `read_file` 返回 File not found，继续用同样路径重复调用会浪费 tool budget 且无法推进。应改用 `find`/`search_files` 确认文件是否存在于其他位置；若确实缺失，将该 unit 标记为 missing 并记录证据，而不是阻塞整批审计。 | 路径漂移常见原因：profile 瘦身、Skill 重命名、官方迁移。处理模式见 `references/batch-readonly-audit-patterns.md`。 |
| **跨 Profile 运行时验证遗漏** | 只检查当前 Profile 的 `skills list`；同一 Skill 在 work-web/default 分别部署时，未分别验证导致运行时不可见 | 按实际部署的每个 Profile 运行 `hermes -p <profile> skills list --enabled-only`，确认目标 Skill 出现且路径符合预期。结果写入 `verification_evidence.runtime_visible` |
| 创建前不查全 | 同名 Skill 多 profile 共存 | 创建前先 find 确认不存在 |
| 跨 Profile 独立复制 | 同一流程出现多个物理副本，修复需要逐个同步且容易漂移 | 单一流程使用官方 `skills.external_dirs` 指向 canonical Skill 包；只有真实业务分叉才复制 |
| **未检查文件完整性就进入诊断** | 占位符/截断文件会误诊为"内容不足"，但真实问题不是 Skill 设计差，而是文件已损坏；强行按常规维度打分并修复会丢失原有专有知识 | 进入 Phase 1 前先用 `read_file` 完整读取并确认：① frontmatter 完整、② 内容不是占位符或截断（无内容行或仅 `... [truncated]` 等）、③ 关键章节存在。若文件截断，优先恢复或重写，而非直接诊断。恢复后仍按 12 维重审。本场景详见 `references/skill-doctor-truncated-skill-recovery.md` |

## Hard Rules

- 不为"看起来完整"把 Skill 变长
- 不加通用人格指令（除非直接影响任务执行）
- 不把触发条件埋在 Skill 深处
- 不多个不相关任务塞一个 Skill
- 不靠关键词触发——描述用户**意图**和**输入类型**
- 不创建"工作助手""写作助手"之类的宽泛 Skill
- 窄而高频 > 宽而全
- 4-8 步可执行流程 > 长篇推理指引
- 输出约定 > 模糊质量目标
- **存在可验证结果的 Skill，不允许在没有定义相应证据时声明"完成"**
- **涉及外部状态变化的 Skill，必须先验证后报告完成**
- **`execution_verification` 必须包含验证对象、验证方法和成功标准；`quality_gate` 使用与风险相称的输出标准或 checklist**
- **Skill 库形状：CLASS-LEVEL  umbrellas，不是窄会话条目。** 每个新 umbrella 必须有一个 rich SKILL.md 和一个 `references/` 目录存放会话级细节。如果一次学习能放进现有 umbrella，就加 references/ 文件或 patch 那个 umbrella，而不是新建一个只对本会话有意义的技能。技能名不能是 PR 号、错误字符串、特性代号、纯库名或 "fix-X/debug-Y/audit-Z-today" 式的一次性工件。
- 一个强 Skill > 多个弱 Skill
- **不审计内置 Skill** — `hermes-agent` 等 Hermes 仓库自带 Skill 不在 `~/.hermes/skills/` 下，在 `~/.hermes/hermes-agent/skills/` 里。批量审计前用 `find ~/.hermes/skills -name SKILL.md` 确认实际自建 Skill 列表，不假设、不混入内置 Skill。子代理审计时必须在 prompt 中明确传入待审 Skill 列表，不靠子代理自己发现。
- **官方/归档边界要先行** — 审计或迁移跨 Profile 同名 Skill 时，先扫描 `~/.hermes/hermes-agent/skills/` 与 `~/.hermes/hermes-agent/optional-skills/` 中的官方同名源，并检查各 Profile 是否存在 `.archived` 旧副本。不把归档目录或官方 optional 版本误迁为自建 canonical。
- **有官方文档的对象必须锚定** — 涉及外部平台/开源工具/协议/OS能力（背后有会维护文档的权威方）的 Skill，必须含官方文档链接 + 查证日期，格式遵循官方最新版；凭记忆写死契约性格式/端点/参数 = 静默失效风险。
