---
name: skill-doctor
description: "Use when creating, auditing, or improving agent Skills. 审核或改造SKILL.md、排查Skill触发与执行问题（如“审一下这个Skill”“诊断为什么没触发”）；不用于普通prompt润色。"
version: 3.9.2
author: Simon
metadata:
  hermes:
    tags: [skills, optimization, review, architecture]
---

# Skill Doctor

审核、创建、优化Skill，使其成为模型能识别、加载、执行并验证的可靠任务控制模块。

## When to Use

- 审查、诊断、改写、简化或重构现有Skill/SKILL.md
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
- `skill-up`是候选真实执行评测后端（[细则](references/skill-up-evaluation-backend.md)），不替代本Skill的架构、语义与安全审计

## Inputs

先自动取得，不让用户重复提供：

1. **先做canonical所有权发现，再写文件**：递归扫描default及全部Profile的同名Skill，并读取各Profile的`skills.external_dirs`。用户说“让多个Profile可用”只表示运行时可见性，**不等于复制多份**。
2. 新建或跨Profile接入前运行：
   ```bash
   SKILL_DOCTOR_DIR="${SKILL_DOCTOR_DIR:-$HOME/.hermes/skills/shared/skill-doctor}"
   TARGET_SKILL_NAME='replace-with-skill-name'
   PYTHONDONTWRITEBYTECODE=1 python3 "$SKILL_DOCTOR_DIR/scripts/check_canonical_ownership.py" \
     --skill-name "$TARGET_SKILL_NAME" --allow-missing
   ```
   - 不传`--profiles`时脚本自动发现`default`及所有存在`config.yaml`的Profile，不维护硬编码Profile名单；只在需要限定范围时才显式传`--profiles a,b`。
   - 已有单一canonical：原地修改并复用`external_dirs`。
   - 尚不存在且多个Profile都需要：优先创建到各目标Profile已经共同加载的shared canonical目录。
   - 只有运行时确实没有共享发现机制、且用户明确接受独立生命周期时，才允许复制；不得把“跨Profile接入”直接翻译成逐目录写入。
   - **整改备份不能落在 skills 树内层**：`cp -Rp` 出的 `xxx.bak-<stamp>` 若留在 `~/.hermes/skills/.../` 里，会被同一脚本当成第二份物理包，使 `ok=false`、报 `multiple_physical_copies` 与各 Profile `visibility_count_2`——这是自己制造的假故障。备份一律放 `~/.hermes/cache/skill-backups/`（或 skills 树外任意目录），再重跑所有权检查确认 `ok=true`；**移出即可，不要删备份**。
3. 用`skill_view`、递归搜索或用户给出的路径读取完整包。
4. 记录用户反馈；没有反馈也可按标准审计。
5. 收集目标Skill的真实使用证据：先根据canonical所有权检查结果确定全部可见Profile，再逐个检索这些Profile的会话历史、运行日志和可用审计记录；覆盖Skill名、别名、description触发语句和实际任务表达，并记录Profile范围、来源、时间窗、命中数与保留期盲区。没有日志不能省略拆分评估，只能把使用证据标为不足。
6. 冻结活动`SKILL.md/references/scripts/templates/assets`清单、行数、字节和hash。
7. 只有目标对象无法定位，或缺失信息会改变目标时才询问。

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
| 1 | **必要性** | 值得独立Skill吗？是否包含应独立路由、执行或验收的多个合同？ |
| 2 | **触发正面** | description是否以动词+任务对象描述目标行为？ |
| 3 | **触发覆盖面** | 是清晰任务类别还是宽泛领域？路由例是否完整？ |
| 4 | **负触发** | 是否排除真实相邻边界，而非靠否定塑形？ |
| 5 | **冲突规则** | 与同类Skill的优先级、差异和移交是否明确？含`overlap_assessment`（见横切门禁） |
| 6 | **输入要求** | 能否主动检索所需信息，不猜也不多问？ |
| 7 | **工作流** | 是否有4–8步可执行流程？机械核心是否合理脚本化？含`loop_assessment`（见横切门禁） |
| 8 | **输出格式** | 诊断、修改和结构化结果是否可预测、可验证？ |
| 9 | **质量标准与验证闭环** | 是否按结果类型定义证据、标准和失败阻断？含`loop_assessment`（见横切门禁） |
| 10 | **简洁性** | 是否渐进披露、无重复/损坏格式、主入口不过载？ |
| 11 | **硬规则 vs Checklist** | 高风险决策是否有主动授权/回滚Checklist？ |
| 12 | **日志与可观测性** | 适用时是否日志优先、路径明确、错误可追踪？ |

详细判据见[12维质量标准](references/quality-dimensions.md)。每个评分必须引用路径+行号/片段。任1个❌或≥3个⚠️进入整改；内容质量与运行影响分开。

### 拆分评估（每个Skill强制执行）

拆分评估属于第1维“必要性”的强制子审计，不新增第13维。必须同时完成两层证据：

1. **使用日志分析**：从真实会话/运行日志提取实际调用，按用户意图、执行分支、输入事实源、风险等级、输出与验收方式归类，观察各职责是经常独立出现、总是共同出现，还是发生误触发/无关加载。记录检索范围和盲区；零命中不等于证明“无需拆分”。
2. **逻辑推演**：把候选职责A/B分别代入“A单独请求、B单独请求、A→B组合、模糊路由、失败/高风险”五类场景，比较其触发、输入、工作流、安全授权、完成标准和维护生命周期是否形成独立执行合同。

必须按下方拆分评估reference的固定schema输出`split_assessment`，字段与必填要求不变。`verdict`只能是：

- `KEEP_SINGLE`：同一意图和完整闭环；
- `KEEP_SINGLE_WITH_REFERENCES`：只是内容多，渐进披露即可；
- `ROUTER_PLUS_CHILDREN`：共享领域入口，但子能力可独立路由和演化；
- `SPLIT_SIBLINGS`：没有必要的共同入口，拆成平级Skill。

详细取证、判定和反过度拆分规则见[Skill瘦身与拆分评估](references/slimming-workflow.md)。

### 循环工程评估（每个Skill强制执行）

循环工程评估属于第7维"工作流"+第9维"质量标准与验证闭环"的强制子审计，不新增第13维。检查对象是Skill执行循环本身的可靠性：失败是否归因并改变策略（而非原样重试）、状态是否可续跑、成功/阻塞/无进展/高风险/预算耗尽五类停止条件、预算硬上限、human_gate、并行隔离。有循环不等于质量高；"无限重试直到看起来成功"判`UNSAFE_LOOP`并阻断完成。纯查询/参考类Skill可判`NOT_APPLICABLE`并说明理由。

必须按下方循环工程reference的固定schema输出`loop_assessment`，字段与必填要求不变。`verdict`只能是：`NOT_APPLICABLE`、`LOOP_COMPLETE`、`LOOP_GAPS`、`UNSAFE_LOOP`。

详细检查项、固定输出schema和典型例子见[循环工程审核](references/loop-engineering-audit.md)；重合评估细则见[重合评估](references/overlap-assessment.md)。

### 重合评估（每个Skill强制执行）

重合评估属于第5维“冲突规则”的强制子审计，不新增第13维。检测被审Skill与库内其他Skill的**实证重合**（越权正文、过期指令、双向漂移），验证冲突规则是否与真实库状态一致。机械层必跑（零LLM token）：`python3 $SKILL_DOCTOR_DIR/scripts/check_cross_skill_overlap.py <目标Skill根目录> --lib ~/.hermes/skills`。
语义层：候选>3个按token区分度取前3，其余记`UNREVIEWED_LOW_SIGNAL`；逐候选五选一裁决（`CANONICAL_HERE`/`CANONICAL_THERE_ADD_ROUTE`/`DUPLICATE_MIGRATE`/`STALE_INSTRUCTION`/`FALSE_POSITIVE`，附路径+行号），必须按重合评估reference的固定schema输出`overlap_assessment`，字段与必填要求不变。完成门禁：无脚本运行证据或存在已读未裁决候选 → 不得报完成。

### 横切门禁

- **职责内聚与拆分**：逐Skill完成`split_assessment`；不能只凭行数、章节数、工具数或主题数判断。日志证据与逻辑推演冲突时，说明冲突及原因；安全边界存在误触发后果时可依据逻辑证据预防性拆分，但必须标明不是日志实证。
- **跨Skill重合**：逐Skill完成`overlap_assessment`；机械层脚本必跑，语义裁决遵守候选上限。`DUPLICATE_MIGRATE`/`STALE_INSTRUCTION`是整改动议不是实施授权，跨Skill迁移需单独确认范围。官方/上游Skill照常产出候选但只记录不改。
- **循环可靠性**：逐Skill完成`loop_assessment`；有迭代执行时必须定义失败归因、停止条件、预算和human_gate。`UNSAFE_LOOP`按❌处理，阻断整改完成；`LOOP_GAPS`按⚠️处理。生产写入、删除、外发、重启类动作永不进入自动循环。
- **行为路由**：修改description、Use/Not Use或冲突规则时，准备明确正例、口语正例、相邻负例、冲突例和加载执行例（[验收细则](references/behavioral-routing-audit.md)）；误触发、重命名或明显重叠时，在新会话/隔离会话真实抽样。未做只能报“静态结构通过”。
- **脚本化**：重复、确定、可验证、人工易漂移的机械步骤优先canonical脚本；语义判断和异常决策留给Agent。脚本须参数/退出码、密钥边界、幂等、日志、PASS/FAIL/边界fixture和失败阻断。
- **完整性**：长输入、批量、分页、多来源分别证明结果正确和输入遍历完整；无命中不等于未读，固定尾部比例不是普适阈值。
- **证据**：自动命中先分类；凭据排除占位符，链接区分真实依赖与代码示例，CLI列表防截断，评分器用已知PASS/FAIL探针（[细则](references/evidence-verification.md)）。
- **安全/生产**：审核完整可执行调用链；禁止换工具/脚本绕过安全拒绝。生产写入、重启、安装、删除、跨Profile修改必须先数字授权并有回滚（[细则](references/safety-production-governance.md)）。
- **官方契约**：有权威维护方的工具/API/协议锚定官方文档和查证日期；内部流程无权威文档时不硬塞。
- **项目绑定型软件Skill**：先做“独立软件资产”分类，只有同时具备独立源码资产、独立维护生命周期、持续发布/部署边界，才转交`software-project-governance`并加载[项目绑定型软件维护Skill门禁](references/project-bound-software-skill-gate.md)。脚本、CLI、SQLite、日志、本地Git、项目路径或域名单独/组合出现都不是充分证据；查询型、操作型、方法型Skill默认仍只做12维审核。Skill Doctor只能报告转交候选，不能自行创建仓库、补项目合同或启动无Skill接管验收。确认进入项目治理后，先建设canonical仓库并完成无Skill接管，再打薄Skill；禁止先删知识。机械预检仅在分类成立后使用`scripts/audit_project_bound_skill.py`。
- **批量治理**：冻结输入全集和canonical；固定12维schema；异步结果由主Agent独立验收；状态`completed`不等于产物完整。

## Phase 2：诊断输出与授权

≤200行Skill用bullet，>200行用table。诊断必须包含：范围、12维评分证据、`split_assessment`、`loop_assessment`、严格verdict、运行影响、根因和整改清单。拆分评估不得只写“建议拆/不拆”，必须分别给出使用日志证据、逻辑推演和证据局限。循环评估不得只写“有/没有循环”，必须覆盖失败归因、停止条件、预算与授权边界。

按本次用户意图分级，不以“文档级”绕过只读要求：

- 用户只要求审核、分析、建议或计划：交付诊断即停止，不写文件。
- 用户要求优化/修复/直接改：范围内低风险文档修订，有备份、diff、测试和回滚即可连续完成，不在诊断后重复索要数字确认。
- Skill拆分、迁移、合并、删除或新增跨Profile范围：须先展示具体动作并取得对应授权；已明确批准同一清单的不重复确认。
- 生产配置、安装、重启、外发及受保护文件遵守各自授权门禁；文档修改若改变这些权限，不属于普通低风险措辞修订。

缺少必要授权时末尾只列1执行/2放弃；本次授权不扩展到未展示的高风险动作。

## Phase 3：修改

若`split_assessment.verdict`为`ROUTER_PLUS_CHILDREN`或`SPLIT_SIBLINGS`，整改清单必须先展示目标Skill边界、触发迁移、共享规则唯一归属、调用链、文件动作和回滚方案；诊断本身不授权创建、移动或删除Skill。

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
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_audit_project_bound_skill.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/audit_skill_package.py . --format json
```

### 完成Checklist

- [ ] 全部修改文件已回读，引用目标存在
- [ ] 记录before/after行数、字节、SKILL hash和包hash
- [ ] 缩减>30%有章节映射、迁移路径、引用和知识保全证据
- [ ] Python/JSON/YAML/Shell等真实语法检查通过
- [ ] 正常、失败、边界fixture通过；失败会阻止完成
- [ ] 每个被审Skill都有完整`split_assessment`，日志来源/窗口/命中数/盲区可核查
- [ ] 每个被审Skill都有完整`loop_assessment`；`UNSAFE_LOOP`未清零前不得报告完成
- [ ] 路由变化已按适用层级验收；发生拆分时A单独、B单独、A→B组合、模糊路由和高风险失败场景全部验证
- [ ] 多Profile可见的Skill已运行`check_canonical_ownership.py`：物理包恰好1份，每个目标Profile运行时恰好命中1份
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

全库/批量流程加载[批量审计与全库治理](references/batch-governance.md)。每个逻辑Skill除完整12维外必须单列`split_assessment`；不能用同名副本数量或文件大小代替职责判断。只在人读报告展开⚠️/❌，机器结果仍保留完整12维；自动评分后随机复核3–5个FAIL/WARN。包hash未变且旧基线合同有效时才继承语义结果，并记录继承/重审/新增数量。

## References

- [12维质量标准](references/quality-dimensions.md)
- [批量审计与全库治理](references/batch-governance.md)
- [Skill瘦身与拆分评估](references/slimming-workflow.md)
- [循环工程审核](references/loop-engineering-audit.md)
- [项目绑定型软件维护Skill门禁](references/project-bound-software-skill-gate.md)

## Hard Rules

- 不为“看起来完整”把Skill变长；主入口只放决策和核心流程
- 不靠关键词触发，不多个无关任务塞一个Skill
- 不因文件长、章节多、脚本多或主题多就拆Skill；先判断是否存在多个独立执行合同
- 不以“日志无命中”证明无需拆分；必须同时完成逻辑推演并标注证据局限
- 不因审计建议自动创建、移动、合并或删除Skill；拆分实施仍受展示清单与授权范围约束
- 不把第10维改名，不新增第13维
- 不让循环靠原样重试冲淡失败信号；`UNSAFE_LOOP`未修复不得报告完成，高风险动作不因进入循环自动获得授权
- 不让脚本/子Agent/静态扫描自证通过
- 不用脚本化、`cross_profile=True`或其他工具扩大授权/绕过安全策略
- 不经明确数字授权删除、移动旧副本或执行生产状态变化
- 不让具体软件项目把Skill当唯一大脑；仓库合同和无Skill接管验收未通过前不打薄项目Skill
