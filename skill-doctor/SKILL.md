---
name: skill-doctor
description: "Use when user asks to create, review, rewrite, debug, simplify, restructure, or improve another Skill, SKILL.md, agent instruction, workflow prompt, or reusable agent capability. Also triggers on: 审一下、审核、改一下这个Skill、看看这个Skill有没有问题、Skill质量、skill-doctor、诊断Skill为什么不触发。Use when user provides a Skill file and asks whether it is good, or wants to diagnose why a Skill is not being triggered."
version: 3.3.0
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
- 判断某活该用 Skill、memory、模板还是工具

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
| 2 | **触发正面** | 有没有明确的 `Use this Skill when the user asks to [动词] [任务对象]`？触发词是具体动词（"部署/重启/配置X"）还是模糊领域（"系统维护"）？ |
| 3 | **触发覆盖面** | 覆盖的是清晰的**任务类别**还是笼统的**领域**？同一个触发条件会不会命中 3 个不同 Skill？ |
| 4 | **负触发** | 有没有写 `Do not use when: [...]`？没有的话会乱触。 |
| 5 | **冲突规则** | 和别的 Skill 撞了怎么办？明确优先级还是让模型猜？ |
| 6 | **输入要求** | 执行前需要哪些信息？没说就得猜，猜就出错。 |
| 7 | **工作流** | 有 4-8 步可执行步骤吗？每步能做（具体命令/操作）？还是抽象描述？ |
| 8 | **输出格式** | 返回什么格式？Markdown/纯文本/JSON？要不要解释？格式是否可验证？ |
| 9 | **质量标准** | 有明确的"这样算好"标准吗？能验证吗？ |
| 10 | **简洁性** | 越短越好。有没有"以防万一"的内容？有没有该进 references/ 却堆在 SKILL.md 里的长代码？**引用数量 >5 个时，检查是否可按使用场景合并：模型能否从引用名判断何时读哪个文件？** |
| 11 | **硬规则 vs Checklist** | 高风险操作是否用了 checklist 而非被动规则？判断公式：**不可逆性 × 前置条件复杂度 × 失败后果严重性**。三者乘积高的场景，硬规则不可靠——agent 会在压力/惯性下把"这是修复"重新框定为规避规则的理由。Checklist 把被动知识变成主动验证——agent 到决策点强制自问，不靠回忆。 |
| 12 | **日志与可观测性** | 判断是否适合加日志：**适合** — Skill 涉及服务重启、配置变更、部署、定时任务、API 调用、进程管理中的任一项；**不适合** — 纯文本生成、翻译、格式转换等不涉及系统状态。如果适合——排障第一步是查日志还是直接猜原因？有没有写明日志路径（如 `<agent-log-path>`、`docker logs <container>`）？评分：✅ 排障第一步查日志 + 有明确路径 / ⚠️ 提到日志但没路径或不是第一步 / ❌ 适合加日志但完全没提 |

**诊断报告质量标准**：每个维度评分必须附具体证据——引用 Skill 原文行号或内容片段，不能只打 ✅ 不说为什么。

**输出诊断时**：≤200 行的 Skill 用 bullet 摘要，>200 行用 table 格式。

### Phase 2: 修改（拿到确认再动手）

**必须等用户确认诊断后再改**，除非用户说了"直接改"。

修改优先级：
1. **先修触发** — 补正面 + 负触发 + 冲突规则，这是可靠性根基
2. **再补工作流** — 把抽象描述变成可执行的 4-8 步，每步带具体命令/操作
3. **定义输出** — 明确格式、语言、是否带解释
4. **加质量门禁** — 改完后的验证步骤
5. **精简长度** — 纯文本说明 → 保留，长代码/示例 → 移到 references/，模板 → 移到 templates/

### Phase 3: 验证（7 问）

1. 模型能判断何时加载吗？
2. 模型能判断何时**不**加载吗？
3. 模型能不猜就能执行吗？
4. 输出格式可预测吗？
5. 够短吗？（能少一行就少一行）
6. 和同类 Skill 冲突了吗？
7. 如果涉及系统变更——改完怎么验证生效？靠日志还是靠猜？

任一回答"否"，回到 Phase 2。

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
| **硬规则的幻觉** | "永远不做X"写在 SOUL 里但 agent 仍然违规 | 高风险操作改用 checklist。详见 [references/anthropic-patterns.md](references/anthropic-patterns.md) |
| **过度限定** | 指令太死，不给模型适应具体场景的空间 | 给信息（what），给灵活性（how）。\"你需要 X 数据\"而非\"你必须用 curl 调 Y API\" |

---

## References（按需加载）

- [references/slimming-workflow.md](references/slimming-workflow.md) — 瘦身工作流：>300 行 Skill 的 5 步拆分流程 + 实战案例
- [references/anthropic-patterns.md](references/anthropic-patterns.md) — Anthropic Skill 实践：Gotchas、Description 写法、渐进式披露、Checklist 决策框架
- [references/cross-profile-sync.md](references/cross-profile-sync.md) — 跨 Profile 同步命令
- [references/quality-dimensions.md](references/quality-dimensions.md) — 质量维度详细说明

---

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
- 一个强 Skill > 多个弱 Skill
