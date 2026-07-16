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

### Step 5: 验证
```bash
# 主文件应该 < 10KB
wc -c SKILL.md
# 所有 references 文件应该被 skill_view 识别
# skill_view(name='xxx') 的 linked_files 应列出所有 references/
# ⚠️ .gitignore 陷阱：如果仓库用 /* 忽略一切再逐个取消忽略目录，
# 新建的 references/ 子目录文件不会被 git 追踪。
# 用 git add -f 强制添加，或验证 git status --short 是否显示新文件。
```

## Step 6: 跨 Profile 瘦身陷阱

当 Skill 在另一个 profile（如 `work-web`）而非当前活跃 profile（如 `default`）时：

- `skill_manage(action='patch')` → ❌ 报错 "Skill not found in active profile"
- `skill_manage(action='write_file')` → ❌ 同样报错
- `write_file` → ❌ 报 "Cross-profile write blocked by soft guard"

**解决方案**：所有 `patch` 和 `write_file` 调用必须加 `cross_profile=True`。

```
patch(mode='replace', path='~/.hermes/profiles/work-web/.../SKILL.md', 
      old_string='...', new_string='...', cross_profile=True)

write_file(path='~/.hermes/profiles/work-web/.../references/new.md', 
           content='...', cross_profile=True)
```

**批量操作顺序**：
1. 先创建所有 references 文件（`write_file` × N，全部 `cross_profile=True`）
2. 再编辑主 SKILL.md（`patch` × N，全部 `cross_profile=True`）
3. 最后 `wc -l` 验证行数

**实战案例**: maishi-crm 从 142KB/2599 行 → 6.2KB/138 行（95.6% 缩减），拆出 4 个 references 文件共 33KB。
**实战案例 2**: maishi-vps-apps 从 828 行 → 612 行（26% 缩减），拆出 6 个 references 文件。跨 profile 操作，全程需 cross_profile=True。
