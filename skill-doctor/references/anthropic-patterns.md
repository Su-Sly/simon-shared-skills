# 从 Anthropic 实践中学到的模式

以下来自 Claude Code 团队在内部跑了几百个 skill 后的经验（[原文](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills)）：

## Gotchas 是 Skill 里信息密度最高的部分

诊断时额外检查：Skill 有没有专门的 Pitfalls/Gotchas 节？这些应该从反复踩坑中积累——"理想情况下，每次模型踩坑就加一条"。**审查已有 Skill 时，如果 Pitfalls 节没有内容，问用户最近遇到什么踩坑没。**

## Description 是给模型看的，不是给人看的

模型在每个会话开始时扫描所有 skill 的 description 来决定"要不要加载"。description 不是摘要，是**触发条件描述**。写的时候问自己："模型看到这个 description，能判断什么时候该用吗？"

## Skill 是文件夹，不只是 Markdown

有效利用文件系统做**渐进式披露**：SKILL.md 只写核心流程 (4-8 步)，详细 API、长配置示例、历史记录分别放进 `references/`、`scripts/`、`assets/`。模型按需读取，主文件保持轻量。

## Skill 可以有自己的"记忆"

Skill 目录里维护一个 log 文件（如 `references/history.log`），每次执行后追加一行摘要。下次运行时模型读到历史，就能对比差异、延续上下文。适用于需要跨会话连续性的 skill（如监控、日报、定期审计）。

## config.json 模式

需要用户提供配置（如 Slack channel、API 端点）的 skill，在目录里放一个 `config.json`，SKILL.md 里写："如果 config.json 不存在，先问用户收集信息再写入。"这样 skill 的安装和配置是一体的。

## Checklist > 硬规则的场景

硬规则是**知识**——agent 知道"永远不做 X"。但 agent 会在惯性/压力下重新框定场景（"我在修代理，不是自主重启"），绕过规则。

Checklist 是**程序**——agent 到决策点被强制自问，不靠记忆：
```
□ 我在操作 gateway 进程？
  → 是 → □ 用户是否通过 Telegram 明确授权？
    → 否 → 停止。告知用户等待授权。
```

**何时用 Checklist（三变量乘积法）：**

```
Checklist 价值 = 不可逆性 × 前置条件复杂度 × 失败后果严重性
```

| 变量 | 低（硬规则即可） | 高（需要 Checklist） |
|------|-----------------|---------------------|
| 不可逆性 | 读文件、搜日志 | 删数据、重启服务、发外部消息 |
| 前置条件 | 单一条件 | 多重条件交叉验证 |
| 失败后果 | 多一轮对话 | 用户断线、数据丢失、对外事故 |

**诊断时检查：** Skill 中有不可逆操作吗？那些操作是用被动规则还是用 checklist 约束的？如果是硬规则，问用户 agent 是否曾违规——违规过的硬规则必须换成 checklist。
