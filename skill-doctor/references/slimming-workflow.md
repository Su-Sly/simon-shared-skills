# 瘦身工作流（Oversized Skill Slimming）

当 SKILL.md > 300 行或 > 50KB 时，按以下步骤瘦身：

## Step 1: 地图绘制
```bash
# 找到所有 section headers
grep -n '^#{1,4} ' SKILL.md
# 查看文件大小
wc -c SKILL.md
```

## Step 2: 识别提取边界
按以下优先级提取（从大到小）：
1. **踩坑记录 / Pitfalls** — 通常是最大块，动辄 500+ 行
2. **详细代码模式 / Code patterns** — antd 拖拽实现、DnD 代码、表单联动等
3. **API 端点表 + 数据库 Schema** — 结构化数据，适合独立文件
4. **第三方集成细节** — Zoho 同步、OAuth 流程、字段映射表
5. **功能特性详细文档** — 仪表盘实现、PWA 配置、移动端适配

## Step 3: 创建 references/ 文件
按**主题**（不是按日期或版本）组织：
- `references/pitfalls-collection.md` — 所有踩坑，按类别分组
- `references/api-endpoints.md` — API 表 + DB Schema
- `references/<module>-guide.md` — 各模块详细指南

每个 references 文件自包含——能独立阅读，不依赖主文件上下文。

## Step 4: 重写 SKILL.md（目标 100-200 行）
保留：
- When to Use / Not to Use（触发条件）
- Architecture 摘要（路径、端口、网络）
- 核心规则（5-8 条，每条一行）
- 部署流程（≤10 行命令）
- 业务模块状态（Phase 列表，每 Phase 1-2 行）
- **关键代码文件表**（文件路径 + 一句话说明）
- **References 表**（指向提取出的文件）
- **Top 5 Pitfalls**（最致命的 5 条，每条一行摘要）
- Version 信息

移除：
- 所有 >20 行的代码块 → references/
- 重复的踩坑记录（同一条坑出现在多处）→ 合并到 references/
- 详细的前端组件实现 → references/
- 完整的 API 端点表格 → references/

## Step 5: 验证
```bash
# 主文件应该 < 10KB
wc -c SKILL.md
# 所有 references 文件应该被 skill_view 识别
# skill_view(name='xxx') 的 linked_files 应列出所有 references/
```

**实战案例**: 某 Skill 从 142KB/2599 行 → 6.2KB/138 行（95.6% 缩减），拆出 4 个 references 文件。
