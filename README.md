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
- 诊断：固定 12 维逐项打分（✅/⚠️/❌），每个评分必须附具体证据
- 修改：触发 → 工作流 → canonical 脚本 → 输出 → 验证 → 渐进式披露
- 验证：区分执行验证、质量门禁和不适用场景，失败时阻止完成声明
- 包级审计器：自动检查 YAML、围栏、链接、维度漂移、脚本语法、凭据线索和包哈希
- 批量治理：冻结输入全集、固定 schema、独立验收子 Agent 结果
- 安全门禁：脚本化不扩大授权，不允许换工具绕过安全策略
- 瘦身工作流：历史材料可逆归档，知识按场景合并到 references

**怎么触发：**

```
审一下这个 Skill
审核一下 xxx Skill 的质量
看看这个 Skill 有没有问题
```

→ [SKILL.md](skill-doctor/SKILL.md)

---

## 📝 更新日志

- [查看中文更新日志](CHANGELOG.md)
- 当前公开版本：`skill-doctor v3.5.0`

---

## 🌟 关于

我是 Simon，外贸行业从业者，也是 AI Agent 的重度用户。这些 Skill 都是在日常使用中踩坑、优化、验证后觉得确实好用才开源出来的。

有问题或建议，欢迎在 Issues 里说一声。

---

[MIT License](LICENSE) · 自由使用 / 修改 / 再分发

Made by [@Su-Sly](https://github.com/Su-Sly)
