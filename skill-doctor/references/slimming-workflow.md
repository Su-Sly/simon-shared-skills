# Skill瘦身工作流

## 触发与目标

出现任一条件就评估瘦身：

- `SKILL.md` >300行或>50KB；
- 主文件链接>10个references且无法按场景快速选择；
- 同一门禁、坑点或历史案例重复出现；
- 旧规则和新规则在活动reference中冲突。

通常目标：主文件120–220行、<25KB。复杂umbrella可超出，但必须说明为什么继续放在主入口，以及拆分会造成什么执行损失。不要为数字机械删知识。

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