# 更新日志

这个仓库按 Skill 版本记录更新。

---

## maishi-docs-mcp v1.0.0 - 2026-09-15

首次公开 MAISHI Docs MCP 使用 Skill。

- 以 OAuth 2.1 授权码 + S256 PKCE 连接为唯一接入方式，不包含密码、Token、Cookie 或客户端密钥。
- 明确“公司管理员先登记 Agent、员工本人再确认一次连接”的边界；不承诺未登记客户端可直接接入。
- 规定按员工当前权限实时访问，先读后改、版本检查、幂等写入和冲突不覆盖。
- 排除服务器维护、生产部署、数据库操作、权限管理和跨系统权威字段写入。

---

## v3.9.2

本次同步已提交的 v3.9.2 通用方法包，不包含本机尚未提交的个性化规则。

### 新增与强化
- 拆分评估：结合真实使用证据与五类逻辑场景，判断保留单一入口、渐进披露、路由子技能或拆为平级技能。
- 循环工程评估：明确失败归因、停止条件、预算、恢复检查点与人工授权边界。
- 跨 Skill 重合评估：新增候选发现脚本、候选上限与 canonical 归属裁决。
- canonical 所有权检查：自动发现多个 Profile，避免重复物理包及运行时重复加载。
- 项目绑定门禁：区分通用方法与独立软件资产，避免过度项目治理。
- 保留固定 12 维审计；结构检查不代替语义判断和真实执行证据。

---

## v3.5.0 - 2026-08-08

这次更新不是继续堆规则，而是对 `skill-doctor` 自身做一次结构治理：把机械检查工程化，把历史规则按场景收敛，并让主入口重新保持可读、可执行。

### 新增
- 新增 canonical 包级审计器 `scripts/audit_skill_package.py`：
  - 校验 YAML frontmatter、description 长度和固定 12 维 schema
  - 检查 Markdown 围栏、真实相对链接、Shell/Python 语法
  - 输出结构化 PASS/WARN/FAIL、退出码、文件清单和包 SHA-256
  - 凭据正则命中只作为线索，不替代语义判断
- 新增 7 个真实 fixture，覆盖正常、失败和边界场景。
- 新增脚本化决策门禁：重复、确定、可验证且人工易漂移的机械步骤优先收敛为单一 canonical 脚本。
- 新增正确性与完整性双验收：批量、分页、多来源任务必须证明输入全集已遍历。

### 重构
- `SKILL.md` 从 339 行压缩到 163 行，保留触发、固定 12 维、核心流程、授权和完成门禁。
- 活动 references 从 31 个收敛为 9 个场景入口：质量维度、行为路由、脚本化、完整性、证据验证、批量治理、安全生产、瘦身和 skill-up 候选。
- 重建损坏的 `quality-dimensions.md`，移除旧 13 维合同和不存在的 `yaml.safe_split` 示例。
- 已有 canonical 文件时改为实际编辑 + diff 摘要 + 验证证据，不再默认在聊天中倾倒完整文件。

### 安全与授权
- `cross_profile=True` 仅限用户明确指定目标 Profile 后使用。
- 删除、移动旧副本、生产写入、重启和外部通讯继续要求数字授权与回滚检查。
- 明确禁止通过脚本、subprocess、cron或其他工具绕过安全策略。

### 验证
- canonical 审计：0 FAIL / 0 WARN。
- 7/7 fixture 通过；缺失链接真实 CLI 探针返回退出码 1。
- default、work、work-web、finance 四个 Profile 均可见且启用。
- 本版本包含 v3.4.19–v3.4.21 的完整性门禁、skill-up 候选记录和脚本化决策门禁。

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
