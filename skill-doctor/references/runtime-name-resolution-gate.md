# Runtime Name Resolution Gate

批量Skill治理不能只验证“文件存在”和`hermes skills list`显示enabled。多个发现根下的同名Skill可能被清单逻辑去重，却让运行时裸名称解析歧义。

## 触发条件

- 全库审计、跨Profile迁移、canonical合并或同名副本治理。
- `skill_view(<bare-name>)`返回ambiguous/not found。
- manifest只有一个逻辑单元，但物理扫描发现多个同名`SKILL.md`。

## 验证流程

1. **物理扫描**：递归扫描default、shared、所有Profile及configured `external_dirs`，按frontmatter `name`分组；不要只按路径basename。
2. **来源分类**：区分canonical、真实业务分叉、官方/Hub安装、`.archived`和备份副本。备份/归档不计活动源。
3. **内容对比**：记录每份路径、字节、行数、SHA-256和关键diff，不能凭mtime猜新旧。
4. **运行时解析**：
   - `hermes -p <profile> skills list`验证预期可见性；
   - 对应Profile里用裸名称加载，确认不会ambiguous；
   - `skills list`的enabled仅是可见性线索，不是唯一解析证据。
5. **收敛重复**：
   - 单一流程保留canonical，其余旧副本先**可逆归档**到活动发现范围之外；
   - 不删除文件，除非用户明确确认；
   - 真实业务分叉必须改成不同名称和触发边界，不能让运行时猜。
6. **回归验证**：归档/改名后再次做四项检查：旧活动路径消失、归档存在、裸名称唯一加载、各Profile预期可见。

## 结果合同

每个同名组至少记录：

```json
{
  "name": "example",
  "physical_paths": [],
  "canonical_path": "...",
  "classification": "duplicate|business-fork|official|archived",
  "runtime_before": "ambiguous|unique|missing",
  "action": "archive|rename|keep",
  "runtime_after": "unique",
  "rollback_path": "..."
}
```

## 陷阱

- manifest按`name`去重后显示“1个逻辑单元”，不代表只有1个物理副本。
- 宽终端下`skills list`完整显示名称，也不代表`skill_view`能唯一解析。
- 把旧副本留在仍被扫描的目录里，只改文件名可能无效；运行时通常按frontmatter `name`识别。
- `.archived`必须确认不在活动发现范围；归档后仍要实际加载验证。
- 子Agent报告“runtime visible”若只引用CLI列表，不足以判PASS。
