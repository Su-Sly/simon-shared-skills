# Skill Doctor：文件截断/占位符修复手记

## 触发场景

批量 Skill 审核或治理时，清单中的 Skill 文件实际内容可能已被压缩成占位符：

- 文件大小异常小（例如原来 31 KB 只剩 1-2 KB）。
- 正文在 frontmatter 后立刻截断为 `... [truncated]` 或 `Use wh...` 等无意义片段。
- 原本存在的架构、部署、数据库门禁、references 映射等章节全部消失。

如果直接套用 12 维评分，会得到"content-accuracy ❌"、"工作流 ❌"、"安全 ❌" 等结论，但这些只是表象。真正的根因是 **文件已损坏/被截断**，必须先恢复文件完整性，再执行常规 Skill Doctor 复审。

## 识别信号

| 信号 | 示例 |
|------|------|
| 行数骤减 | 原本数百行，现在 < 20 行 |
| 内容被截断 | 行尾 `...`、`.[truncated]`、英文乱码片段 |
| 章节缺失 | 没有 When to Use/Not、Architecture、Workflow、Verification Pattern 等 |
| references 文件存在但 SKILL.md 不再引用 | 说明文件原本完整 |
| `read_file` 显示 `truncated: false` 但内容明显不完整 | 内容被覆盖过，不是读取截断 |

## 处理流程

1. **先不要写诊断报告**。暂停 Phase 1，把文件状态标记为 `truncated`。
2. **读取完整文件并确认**。调用 `read_file` 看是否确实是占位符；不是读取工具的问题。
3. **搜索相邻文件**：
   - 同一目录下的 `references/` 目录。
   - 其他 profile 下是否存在同名或同族 Skill 的完整副本。
   - 历史 session 记录（不当作主要证据，但可作为辅助）。
4. **决定恢复策略**：
   - 若 references 丰富且能重构出完整 SKILL.md → 重写 SKILL.md，保留所有专有知识，长内容继续引用 references。
   - 若无法重构 → 标记该 Skill 需要用户人工提供基线，不要凭空编造。
5. **重写后自验**：
   - 完整回读 SKILL.md。
   - 检查所有 references 链接真实存在。
   - 按 12 维重新评分，确认 0 ❌ 0 未处理 ⚠️ 才标 PASS。
6. **报告特殊**。在最终 JSON 中记录 `files_changed` 为 `SKILL.md`，并说明修复类型是 `truncated-skill-recovery`，而不是普通微调。

## 应用维护类 Skill 的恢复要点

截断的应用维护 Skill（如 `maishi-crm`）恢复时，必须一次性重建以下安全规范：

- Git 权威源：本地 edit → push → VPS `deploy.sh`。
- 禁止 VPS 直改、禁止常规 `docker cp` 热补丁、禁止生产服务器打 tag。
- 数据库破坏性命令 6 步门禁：backup → diff → numeric confirmation → execute → rollback → verify。
- Verification Pattern：Action / Target / Method / Success Criteria / Completion Rule。
- 对 `maishi-crm` 这类系统，必须引用已有的 `references/` 文件（如 `backend-db-pattern.md`、`api-endpoints.md`、`zoho-sync-guide.md`、`packing-module.md` 等），避免把数万字专有知识塞回 SKILL.md。

## 与常规 Skill Doctor 流程的区别

| 常规流程 | 截断恢复流程 |
|----------|--------------|
| 直接 12 维评分 | 先判断文件完整性 |
| 诊断 → 用户确认 → 小修 | 直接重写（因为文件已不可用） |
| 修改后重点验证格式 | 重点验证 references 存在和专有知识未丢失 |
| 报告为"优化" | 报告为"恢复 + 优化" |

## 验证清单

- [ ] 回读 SKILL.md 全文，确认无截断。
- [ ] 所有 references 链接已用 `read_file` 或 `search_files` 确认存在。
- [ ] 12 维复审后 0 ❌ 0 未处理 ⚠️。
- [ ] 应用维护 Skill 的 Git 权威源与数据库门禁已加入。
- [ ] 最终 JSON 报告标注 `truncated-skill-recovery` 类型。
