# 🧰 Simon Shared Skills

#### 我在用 Hermes Agent 过程中积累的 AI Skill，挑实用的开源出来

[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

都是自己每天在用的，跑通了一段时间确实省事，才搬出来开源的。

这里的每个 Skill 都是 Agent 能直接加载的结构化指令集。Claude Code、Codex、Hermes Agent 等支持 SKILL.md 的 Agent 都能装。

---

## 📋 目录

| 名字 | 一句话 |
| --- | --- |
| 🩺 **skill-doctor** | 审计、创建、优化 AI Agent Skill 的 12 维度诊断框架 |

---

## 📦 安装方式

在支持 Skill 的 Agent 里，直接说：

```
帮我安装这个 skill：https://github.com/Su-Sly/simon-shared-skills/tree/main/skill-doctor
```

Agent 会自己 clone 到对应目录，不用你操心路径。

---

## ✨ Skills

### 🩺 skill-doctor

*"Skill 写完了不知道好不好？跑一遍诊断就知道了。"*

12 维度审计框架，把一个 Skill 从"能用"变成"可靠"。覆盖触发条件、负触发、冲突规则、工作流可执行性、输出格式、质量标准、简洁性、硬规则 vs Checklist、日志与可观测性等维度。

**核心能力：**
- 诊断：12 维度逐项打分（✅/⚠️/❌），每个评分必须附具体证据
- 修改：5 级优先级（先修触发 → 再补工作流 → 定义输出 → 加质量门禁 → 精简长度）
- 验证：7 问检查模型能否识别、加载、执行
- 瘦身工作流：>300 行 Skill 的 5 步拆分流程
- 反模式速查：7 种常见 Skill 问题 + 修复方案
- Anthropic 实践：Gotchas、Description 写法、渐进式披露、Checklist 决策框架

**怎么触发：**

```
审一下这个 Skill
审核一下 xxx Skill 的质量
看看这个 Skill 有没有问题
```

→ [SKILL.md](skill-doctor/SKILL.md)

---

## 🌟 关于

我是 Simon，外贸行业从业者，也是 AI Agent 的重度用户。这些 Skill 都是在日常使用中踩坑、优化、验证后觉得确实好用才开源出来的。

有问题或建议，欢迎在 Issues 里说一声。

---

[MIT License](LICENSE) · 自由使用 / 修改 / 再分发

Made by [@Su-Sly](https://github.com/Su-Sly)
