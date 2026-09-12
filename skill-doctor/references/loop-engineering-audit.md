# 循环工程审核（Loop Engineering）

拆分评估回答"职责边界是否正确"；本门禁回答"**该Skill的执行循环本身是否可靠**"。它属于第7维"工作流"与第9维"质量标准与验证闭环"的强制子审计，不新增第13维。

## 1. 定位与适用性

Skill Doctor 自身的`诊断→修改→测试→失败修复→复审`已经是半套循环工程；本门禁把"循环本身"变成被审对象。每个被审Skill必须完成`loop_assessment`，但`applicable=false`是合法结论：

- 纯查询、参考知识、单步转换类Skill：无迭代执行，判`NOT_APPLICABLE`并说明理由。
- 多步整改、批量处理、部署验收、评测回归、监控闭环类Skill：必须完整评估。

有循环不等于质量高。以下模式必须判失败：

```
执行失败 → 原样重试 → 再失败 → 继续重试（无失败归因、无策略变化）
无限循环直到"看起来成功"
```

合格循环的最小形态：

```
执行 → 观察真实结果 → 定位失败类型 → 改变下一轮策略 → 独立验证 → 达成停止条件
```

## 2. 检查项

| 字段 | 检查问题 |
|---|---|
| `applicable` | 是否存在真实迭代执行？不适用时理由是否成立？ |
| `goal` | 循环最终要达成什么，成功如何定义？ |
| `state` | 进度保存在哪里？会话中断/压缩后能否从检查点续跑？ |
| `observe` | 每轮读取什么真实结果（日志/退出码/API回读/hash），还是只看自报？ |
| `grader` | 谁依据什么标准判定本轮通过？评分器是否用已知PASS/FAIL探针自验？ |
| `feedback` | 失败证据是否真的改变下一轮动作？还是同参数机械重试？ |
| `stop_conditions` | 成功、阻塞、无进展、高风险、预算耗尽五类停止条件是否都定义？ |
| `budget` | 最大轮数、时间、成本、外部API调用量是否有硬上限？ |
| `human_gate` | 哪些状态不能自动跨越（生产写入、删除、外发、重启、新增范围）？ |
| `isolation` | 并行Agent/worker是否有worktree、锁或任务租约，避免互踩同一工作树？ |

## 3. 固定输出

```yaml
loop_assessment:
  applicable: true | false
  applicability_rationale: ""
  goal: ""
  state_checkpoint: ""
  observe: ""
  grader: ""
  feedback_mechanism: ""
  stop_conditions:
    success: ""
    blocked: ""
    no_progress: ""
    high_risk: ""
    budget_exhausted: ""
  budget: ""
  human_gate: []
  isolation: ""
  verdict: NOT_APPLICABLE | LOOP_COMPLETE | LOOP_GAPS | UNSAFE_LOOP
  rationale: []
  confidence: high | medium | low
```

verdict判定：

- `NOT_APPLICABLE`：无迭代执行，理由成立。
- `LOOP_COMPLETE`：observe/feedback/stop/budget/human_gate五要素齐全，反馈改变策略而非重试。
- `LOOP_GAPS`：有循环但缺停止条件、预算、状态续跑或失败归因（⚠️级，落入第7/9维）。
- `UNSAFE_LOOP`：循环可自动跨越授权边界、无进展仍不停止、或用机械重试冲淡失败信号（❌级，阻断整改完成）。

## 4. 评分归属

- 第7维"工作流"：循环步骤是否可执行、状态可续跑、预算与停止条件是否定义、并行是否隔离。
- 第9维"验证闭环"：observe是否真实证据、grader是否独立、feedback是否改变策略、失败是否阻断完成。
- 第11维联动：human_gate缺失且循环含高风险动作时，同时触发硬规则Checklist缺陷。

## 5. Skill Doctor 自身的循环要求

对skill-doctor自审或整改时，除通用检查外还须满足：

1. 冻结被审Skill基线（清单、行数、字节、hash）后再动手。
2. 诊断12维并定位具体失败，只修对应失败。
3. 每轮修改后运行结构测试、失败样本、边界样本与行为路由测试，将失败证据写入下一轮。
4. 停止条件：`0 FAIL / 0未接受WARN`即停；连续两轮无进展或触发安全/授权边界即停并报告。
5. 禁止靠重复改措辞、重复跑同一测试制造"循环已完成"的假象。
6. 生产写入、删除、外发、重启类动作永不进入自动循环，每次单独授权。

## 6. 典型例子

- ✅ 整改循环：FAIL→定位根因→修改→重跑测试→独立复核→0 FAIL停止；中断后从检查点清单续跑。
- ❌ 部署循环：服务起不来就无限restart直到碰巧健康；无预算、无根因记录。
- ❌ 抓取循环：分页失败只重试同一页20次，不区分限流/改版/网络，额度耗尽无停止条件。
- ⚠️ 批量审核循环：有进度文件可续跑，但未定义"连续N个单元无进展"的停止条件。
