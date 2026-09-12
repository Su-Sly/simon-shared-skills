# Skill瘦身工作流

## 触发与目标

出现任一条件就评估瘦身：

- `SKILL.md` >300行或>50KB；
- 主文件链接>10个references且无法按场景快速选择；
- 同一门禁、坑点或历史案例重复出现；
- 旧规则和新规则在活动reference中冲突。

通常目标：主文件120–220行、<25KB。复杂umbrella可超出，但必须说明为什么继续放在主入口，以及拆分会造成什么执行损失。不要为数字机械删知识。

## 拆分评估：日志证据 + 逻辑推演

拆分的对象不是“主题”，而是执行合同。每个被审Skill都必须完成本节；它属于第1维“必要性”，不是新维度。

### 1. 收集真实使用证据

优先读取可追溯的真实调用，不让Skill正文替自己证明用途：

1. 检索会话历史、运行日志和已有审计记录，查询Skill名、别名、description触发短语及用户真实任务表达；需要时包含user/assistant/tool角色，避免只找到讨论而漏掉实际加载与执行。
2. 时间窗默认覆盖当前可用保留期，并至少说明起止时间；若Skill近期有大版本变更，同时区分变更前后。不得声称超出日志保留期的全量结论。
3. 每个命中归类：`user_intent`、`workflow_branch`、`input_sources`、`risk_authorization`、`output_verification`、`co_occurring_responsibilities`、`misroute_or_unused_context`。
4. 去重同一任务的重试、压缩续会话和转述记录；讨论Skill不算使用，除非实际加载并执行目标能力。
5. 输出来源、时间窗、原始命中数、去重后调用数和盲区。零命中只能记`usage_evidence.status=none`，不能推导“无需拆分”。

日志重点回答：

- A、B是否被用户分别单独请求？
- A、B是否总是同一任务的连续阶段？
- 加载B的规则是否曾干扰只做A的任务？
- 是否发生误触发、错误移交、错误授权或拿错验收标准？
- 某分支是否长期不使用，实际上只是reference或脚本？

### 2. 逻辑推演候选边界

先从When to Use、工作流分支、安全门禁、输入源和完成规则提出候选职责A/B，再强制推演五类场景：

1. **A单独请求**：不加载B能否完整执行并验收？
2. **B单独请求**：不加载A能否完整执行并验收？
3. **A→B组合**：拆分后能否清晰移交状态，不产生双重canonical？
4. **模糊路由**：用户只说领域词时，由谁接住，是否需要薄router？
5. **失败/高风险**：A失败会否误触B的写入、删除、重启或外部通讯权限？

对A/B逐项比较：用户意图、输入事实源、工作流骨架、安全/授权、输出与完成标准、维护/发布生命周期、共享状态和知识重复成本。

### 3. 判定

- `KEEP_SINGLE`：A/B是同一目标的连续阶段，共享状态、安全边界和完成标准；拆分只会增加移交和漂移。
- `KEEP_SINGLE_WITH_REFERENCES`：执行合同一致，只是正文过长、平台细节或案例过多；把细节移入references或scripts。
- `ROUTER_PLUS_CHILDREN`：用户认识一个总领域，但下面存在可独立触发、执行、验收和演化的能力；入口只做路由，不复制子Skill合同。
- `SPLIT_SIBLINGS`：A/B可独立路由且没有必要的共同入口，安全/流程/验收或生命周期存在实质分叉。

支持拆分通常需要“独立用户意图”加至少一项实质分叉；但若混放会跨越高风险授权边界，可依据逻辑证据预防性拆分。此时必须标注`evidence_basis=logical_safety`，不能伪称日志已验证。

反过来，以下都不是充分理由：行数多、章节多、用了多个工具、有多个脚本、同一产品含前后端、一个流程包含发现/修改/验证阶段。

### 4. 固定输出

```yaml
split_assessment:
  usage_evidence:
    status: sufficient | partial | none
    sources: []
    time_window: ""
    raw_matches: 0
    deduplicated_invocations: 0
    limitations: []
  observed_intents: []
  candidate_boundaries: []
  logical_simulation:
    a_only: ""
    b_only: ""
    combined: ""
    ambiguous_routing: ""
    failure_or_high_risk: ""
  verdict: KEEP_SINGLE | KEEP_SINGLE_WITH_REFERENCES | ROUTER_PLUS_CHILDREN | SPLIT_SIBLINGS
  rationale: []
  evidence_basis: observed | mixed | logical_safety | logical_only
  confidence: high | medium | low
  limitations: []
```

如果建议拆分，再输出候选Skill的description边界、唯一canonical归属、共享规则放置点、调用/移交关系、迁移与回滚计划。审计建议不等于实施授权。

## 1. 建立地图与快照

- 记录完整文件清单、行数、字节、SHA-256和包hash。
- 完整读取或建立章节/引用清单；工具分页不等于源文件截断。
- 创建可验证快照，确认文件集合与hash一致后再改。

## 2. 分类内容

主文件保留：

- description、When to Use/Not to Use、冲突规则和输入获取；
- 权威维度/合同；
- 4–8步核心工作流；
- 授权、失败阻断和完成规则；
- 少量按使用场景组织的reference入口。

移入references：

- 详细判据、长表格、完整代码示例；
- 批量治理、跨Profile、生产安全等专项流程；
- 历史案例中已提炼出的可复用经验。

可逆归档：

- 日期/批次命名的原始报告；
- 已被新权威文档吸收的旧版速查；
- 与现行合同冲突但仍有追溯价值的材料。

## 3. 合并原则

- 按使用场景合并，不按日期/版本堆文件。
- 每条知识建立“旧文件/章节 → 新文件/章节或归档路径”映射。
- 不把多个无关主题合并成新的百科。
- 真实Markdown链接必须存在；示例链接放在inline/fenced code中。

## 4. 跨Profile边界

`cross_profile=True`不是默认方案。只有用户明确指定目标Profile和修改范围后才可使用：

1. 展示目标文件、动作、快照和回滚。
2. 获得数字授权。
3. 写入后完整回读并运行目标Profile验证。
4. 删除或移动旧副本需要清单内明确授权；未授权时只报告，不删除。

## 5. 验证

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_audit_skill_package.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/audit_skill_package.py . --format json
```

同时验证：

- before/after行数、字节、SKILL hash和包hash；
- 缩减>30%时有章节映射、迁移目标、引用存在和知识未丢失证据；
- `skill_view`全文回读和linked files；
- `hermes skills list --enabled-only`运行时可见；
- 12维语义复审无新增FAIL/WARN。

任一失败则修复或从快照回滚，不报告整改完成。