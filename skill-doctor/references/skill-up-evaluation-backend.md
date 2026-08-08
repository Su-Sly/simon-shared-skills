# skill-up 评测后端候选

状态：**候选，暂不安装**
查证日期：2026-08-08

## 定位

- 官方仓库：https://github.com/alibaba/skill-up
- 官方手册：https://alibaba.github.io/skill-up/zh/
- 维护方：Alibaba GitHub Organization
- 许可证：Apache-2.0
- 查证版本：v0.7.0

`skill-up` 是 Agent Skill 的真实执行评测 CLI，不是单独的优化提示词。它负责把目标 Skill 安装到真实 Agent Engine，运行声明式测试用例，再由规则、脚本或 Agent Judge 判分并生成报告。

仓库另附 `skill-upper` Agent Skill，负责创建评测、分析失败、修改目标 Skill/测试用例并循环回归。两层关系：

```text
skill-upper（理解、诊断、迭代）
  → skill-up CLI（执行与报告）
  → Codex / Claude Code / Qoder / Qwen Code
  → rule_based / script / agent_judge
```

## 与 Skill Doctor 的关系

不替代 Skill Doctor：

- Skill Doctor：12维结构/语义审计、跨 Profile 治理、安全与完成门禁。
- skill-up：真实 Agent 行为测试、多引擎比较、持久回归用例、CI 报告。

未来合理位置是 Skill Doctor 的“真实执行后端”：静态/语义审计与授权整改后，用 skill-up 验证正向触发、口语触发、相邻负例、冲突路由、长输入完整性及产物真实性。

## 当前不安装的理由

- 建立有效 eval case 的成本高，不适合无差别覆盖全库。
- 每次真实运行消耗模型额度；Agent Judge 还会增加额外调用。
- 自动演进可能把错误评分器或错误用例当成目标，必须保留主 Agent 独立复核。
- 2026-08-08 已知上游问题：路由专项评测仍在 Issue #166；确定性断言增强仍在 #165；Codex JSONL 单行超过 1 MiB 可能静默截断（#172）；跨协议 agent_judge 存在 #104。

## 重新评估触发条件

满足任一项时重新评估安装：

1. 需要对高价值 Skill 做可重复的真实 Agent 回归，而隔离会话手工组织成本明显升高。
2. 需要比较同一 Skill 在 Codex、Claude Code 等多引擎上的行为差异。
3. 需要把关键 Skill 测试接入 GitHub Actions。
4. 上游关闭或有效规避 #166、#172 等与路由/长输出相关问题。

首次 POC 优先选输入输出可确定性验收、外部副作用低的 Skill；不从全库批量接入开始。评测必须同时检查正确性与完整性，评分器须用已知 PASS/FAIL 探针自验。
