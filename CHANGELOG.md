# 更新日志

这个仓库目前只公开 `skill-doctor`，所以更新日志按版本直接记录。

---

## v3.4.0 - 2026-07-16

这次更新的核心不是“多加一点说明”，而是把**验证闭环**从建议升级成 Skill 的硬门禁。

### 新增
- 新增 **Verification Pattern** 五要素：
  - Action
  - Verification Target
  - Verification Method
  - Success Criteria
  - Completion Rule
- 新增 **Phase 3B：自身修改验证**，要求改 Skill 的 agent 先验证自己的修改，再报告完成。
- 新增 **批量审计模式** 说明：
  - 批量审多个 Skill 时，只输出有问题的维度
  - 汇总高频问题，识别系统性缺口
- 新增 **实战踩坑** 小节，明确常见误区与后果。
- 新增 3 个 references：
  - `references/v3.4.0-verification-pattern.md`
  - `references/batch-audit-patterns.md`
  - `references/cross-profile-sync.md`

### 强化
- 把原来的“质量标准”升级为 **质量标准与验证闭环**，不再只看“写得像不像”，而是看“有没有证据证明完成”。
- 把“加质量门禁”改为 **加验证闭环**，要求涉及外部状态变化的 Skill 必须定义验证动作。
- 强化简洁性维度，补充格式卫生检查：
  - description 长度
  - fence 是否配对
  - 是否存在空 code block
- 强化日志与可观测性维度，明确：
  - 适合加日志的场景
  - 日志必须给出具体路径或方法
  - 排障第一步应先看日志，不靠猜
- 强化 Hard Rules，明确：
  - 没有可验证证据，不允许声明完成
  - 涉及外部状态变化，必须先验证后报告完成
  - Verification 必须写清验证对象、方法、成功标准
  - 批量审计时不要混入 Hermes 内置 Skill

### 更新
- 更新 `references/slimming-workflow.md`：
  - 补充 Git 跟踪新 `references/` 文件的坑
  - 补充跨 Profile 瘦身时 `cross_profile=True` 的要求
  - 增加第二个实战案例

### 兼容性说明
- 这是在 `v3.3.0` 基础上的向前增强，核心 12 维度框架保留。
- 变化重点在于：**把“验证”从附属说明提升为完成标准本身。**

---

## v3.3.0 - 初始公开版
- 首次开源 `skill-doctor`
- 提供 12 维度 Skill 审计框架
- 包含基础反模式速查与瘦身工作流
