---
name: skill-doctor
description: "Use when user asks to create, review, rewrite, debug, simplify, restructure, or improve another Skill, SKILL.md, agent instruction, workflow prompt, or reusable agent capability. 触发：审一下、审核、改一下这个Skill、看看这个Skill有没有问题、Skill质量、skill-doctor、诊断Skill为什么不触发。"
version: 3.5.0
author: Simon
metadata:
  hermes:
    tags: [skills, optimization, review, architecture]
---

# Skill Doctor

审核、创建、优化Skill，使其成为模型能识别、加载、执行并验证的可靠任务控制模块。

## When to Use

- 审查、诊断、改写、简化或重构现有Skill/Agent指令
- 创建新Skill并设计触发、工作流和验证合同
- Skill触发不稳定、执行不一致、输出混乱或与其他Skill冲突
- 判断某项知识应进入Skill、memory、模板、脚本还是普通工具

## When Not to Use

- 普通写作、翻译、编码、商务分析
- 仅因文本含“指令”就调用；对象必须是可复用Agent能力

## Conflict Rules

- 创建新Skill且重点是Hermes frontmatter/入库规范：优先`hermes-agent-skill-authoring`
- 审核或优化已有Skill：使用本Skill
- 实现业务代码：交给对应开发Skill；本Skill只管Skill质量
- `skill-up`是候选真实执行评测后端，不替代本Skill的架构、语义与安全审计

## Inputs

先自动取得，不让用户重复提供：

1. 用`skill_view`、递归搜索或用户给出的路径读取完整包。
2. 记录用户反馈；没有反馈也可按标准审计。
3. 冻结活动`SKILL.md/references/scripts/templates/assets`清单、行数、字节和hash。
4. 只有目标对象无法定位，或缺失信息会改变目标时才询问。

文件疑似截断/占位时先恢复或阻断，不用残缺内容做常规评分。

## Phase 1：诊断

先运行只读结构审计，再做语义判断：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/audit_skill_package.py /absolute/path/to/skill --format json
```

脚本结果只是结构证据；正则、字符串计数、脚本success和子Agent自报不能替代语义审计。

按固定12维逐项评分。维度ID和名称必须恰好为1–12：

| # | 维度 | 核心检查 |
|---|---|---|
| 1 | **必要性** | 值得独立Skill吗？是否混入无关职责？ |
| 2 | **触发正面** | description是否以动词+任务对象描述目标行为？ |
| 3 | **触发覆盖面** | 是清晰任务类别还是宽泛领域？路由例是否完整？ |
| 4 | **负触发** | 是否排除真实相邻边界，而非靠否定塑形？ |
| 5 | **冲突规则** | 与同类Skill的优先级、差异和移交是否明确？ |
| 6 | **输入要求** | 能否主动检索所需信息，不猜也不多问？ |
| 7 | **工作流** | 是否有4–8步可执行流程？机械核心是否合理脚本化？ |
| 8 | **输出格式** | 诊断、修改和结构化结果是否可预测、可验证？ |
| 9 | **质量标准与验证闭环** | 是否按结果类型定义证据、标准和失败阻断？ |
| 10 | **简洁性** | 是否渐进披露、无重复/损坏格式、主入口不过载？ |
| 11 | **硬规则 vs Checklist** | 高风险决策是否有主动授权/回滚Checklist？ |
| 12 | **日志与可观测性** | 适用时是否日志优先、路径明确、错误可追踪？ |

详细判据见[12维质量标准](references/quality-dimensions.md)。每个评分必须引用路径+行号/片段。任1个❌或≥3个⚠️进入整改；内容质量与运行影响分开。

### 横切门禁

- **行为路由**：修改description、Use/Not Use或冲突规则时，准备明确正例、口语正例、相邻负例、冲突例和加载执行例；误触发、重命名或明显重叠时，在新会话/隔离会话真实抽样。未做只能报“静态结构通过”。
- **脚本化**：重复、确定、可验证、人工易漂移的机械步骤优先canonical脚本；语义判断和异常决策留给Agent。脚本须参数/退出码、密钥边界、幂等、日志、PASS/FAIL/边界fixture和失败阻断。
- **完整性**：长输入、批量、分页、多来源分别证明结果正确和输入遍历完整；无命中不等于未读，固定尾部比例不是普适阈值。
- **证据**：自动命中先分类；凭据排除占位符，链接区分真实依赖与代码示例，CLI列表防截断，评分器用已知PASS/FAIL探针。
- **安全/生产**：审核完整可执行调用链；禁止换工具/脚本绕过安全拒绝。生产写入、重启、安装、删除、跨Profile修改必须先数字授权并有回滚。
- **官方契约**：有权威维护方的工具/API/协议锚定官方文档和查证日期；内部流程无权威文档时不硬塞。
- **批量治理**：冻结输入全集和canonical；固定12维schema；异步结果由主Agent独立验收；状态`completed`不等于产物完整。

## Phase 2：诊断输出与授权

≤200行Skill用bullet，>200行用table。诊断必须包含：范围、12维评分证据、严格verdict、运行影响、根因和整改清单。

默认诊断后停止，末尾只列：

1. 直接改
2. 不改，放弃本轮整改

用户明确“直接改”“1”“全部直接改”后，授权只覆盖已展示清单。新增删除、外部通讯、生产动作或其他Profile范围需重新确认。

## Phase 3：修改

按以下顺序精准修改：

1. 修正触发、负触发和冲突边界。
2. 补输入获取与4–8步工作流。
3. 将稳定机械步骤收敛为单一canonical脚本，不复制batch脚本。
4. 定义输出、验证类型和完成规则。
5. 将详细判据/案例移入按使用场景组织的references；历史原始报告可逆归档。
6. 清理本次改动产生的孤儿引用/import；既有无关死内容只报告不顺手删。

有canonical文件时实际编辑文件并交付diff/证据；仅用户要草稿或无法访问文件时输出完整SKILL.md。

## Phase 4：验证

### 结构与脚本

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_audit_skill_package.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/audit_skill_package.py . --format json
```

### 完成Checklist

- [ ] 全部修改文件已回读，引用目标存在
- [ ] 记录before/after行数、字节、SKILL hash和包hash
- [ ] 缩减>30%有章节映射、迁移路径、引用和知识保全证据
- [ ] Python/JSON/YAML/Shell等真实语法检查通过
- [ ] 正常、失败、边界fixture通过；失败会阻止完成
- [ ] 路由变化已按适用层级验收
- [ ] 跨Profile按实际目标逐个`config check`和运行时加载
- [ ] `skill_view`完整回读；Hermes运行时裸名称唯一可见
- [ ] 用同一12维复审，新增FAIL/WARN为0

任一项未确认，不报告整改完成；验证失败自动修复或明确阻塞。

## Verification Pattern

- `execution_verification`：Action、Target、Method、Success Criteria、Completion Rule五元素齐全。
- `quality_gate`：定义与风险相称的格式/内容checklist。
- `not_applicable`：说明为什么没有待验收结果。

审计完成只表示范围、证据和报告已生成；治理完成要求授权范围内FAIL全部修复，未接受WARN仍列未完成。最终拆分`audit_execution`、`runtime_integrity`、`content_quality`、`external_system_status`和`overall`。

## Batch Mode

全库/批量流程加载[批量审计与全库治理](references/batch-governance.md)。只在人读报告展开⚠️/❌，机器结果仍保留完整12维；自动评分后随机复核3–5个FAIL/WARN。包hash未变且旧基线合同有效时才继承语义结果，并记录继承/重审/新增数量。

## References

- [12维质量标准](references/quality-dimensions.md)
- [行为路由验收](references/behavioral-routing-audit.md)
- [脚本化决策门禁](references/scriptization-decision-gate.md)
- [完整性与覆盖性](references/coverage-completeness-gate.md)
- [审计证据与验证闭环](references/evidence-verification.md)
- [批量审计与全库治理](references/batch-governance.md)
- [安全、生产与委派验收](references/safety-production-governance.md)
- [Skill瘦身工作流](references/slimming-workflow.md)
- [skill-up评测后端候选](references/skill-up-evaluation-backend.md)

## Hard Rules

- 不为“看起来完整”把Skill变长；主入口只放决策和核心流程
- 不靠关键词触发，不多个无关任务塞一个Skill
- 不把第10维改名，不新增第13维
- 不让脚本/子Agent/静态扫描自证通过
- 不用脚本化、`cross_profile=True`或其他工具扩大授权/绕过安全策略
- 不经明确数字授权删除、移动旧副本或执行生产状态变化
- 不把“审计完成”简写成“治理完成”
