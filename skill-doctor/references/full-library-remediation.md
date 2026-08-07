# 全库 Skill 连续治理工作流

用于用户明确要求“审核并优化所有自建 Skill”的场景。这里的目标不是生成审计报告，而是把整个运行时本地 Skill 库持续整改到可验收状态。

## 1. 锁定真实范围

不要把文件系统里的 `SKILL.md` 数量当作逻辑 Skill 数量。各 Profile 可能有重复副本、共享源、官方派生副本和归档目录。

1. 枚举当前所有 Profile。
2. 对 default 和每个 Profile 分别运行宽终端清单，避免 Rich 表格用 `…` 截断长名称：
   ```bash
   COLUMNS=320 NO_COLOR=1 hermes skills list
   COLUMNS=320 NO_COLOR=1 hermes -p <profile> skills list
   ```
3. 取所有运行时启用且 `Source=local` 的并集；排除 `builtin`、`plugin`、Hub 安装和归档资产。
4. 按名称、canonical 路径和文件 hash 去重：
   - 同名同 hash：一个逻辑单元。
   - 同名不同 hash：保留为独立分叉，分别审核。
5. 用递归文件扫描补充路径和 package 内容，但不能反过来用物理文件数覆盖运行时范围。

## 2. 修改前快照

- 为每个最终 canonical package 保存完整目录快照和索引。
- 索引至少记录：name、canonical path、全部运行时 Profile、SHA256、备份路径。
- 不删除 Skill；重命名、归档、合并仍需单独确认。

## 3. 连续整改队列

用户已明确说“所有都审核并优化”时，这就是整个范围的 Phase 2 授权：

- 不再逐 Skill 或逐批确认。
- 不把内部批次包装成对用户的 Phase 1/2/3。
- 内部可以并行分组，但它只是调度细节；必须自动持续排空整个队列。
- 按主文件+references总行数均衡工作量，不能只按 Skill 数量平均；一个 2600 行 Skill 不能和普通 100 行 Skill等价计数。

每个逻辑单元固定执行：

```text
读取完整 SKILL.md 与必要 references
→ Skill Doctor 12维与架构一致性诊断
→ 修复全部真实 FAIL/WARN
→ 完整回读修改文件
→ 检查全部引用存在
→ 同规则重新审核
→ 验证相关 Profile 运行时可见
```

应用维护 Skill 额外检查：Git 权威源是否与 VPS 直改、SCP/rsync、`docker cp` 热补丁、生产服务器 commit/tag 冲突；数据库 `--accept-data-loss`、reset/drop/force 是否有备份、diff、数字确认和回滚门禁。

## 4. 子 Agent 交付合同

子 Agent 只负责不重叠的 canonical 路径，必须写可回读的结构化结果文件，至少包含：

- `name`
- `path`
- `files_changed`
- `before_findings`
- `after_verdict`
- `after_fail_count`
- `after_warn_count`
- `verification_evidence`

`completed`状态和文字自述都不算完成。主 Agent必须读取结果文件、回读真实canonical文件并重新验收。

## 5. 验收结果失效与安全停点

### 验收失效

结构化PASS只对应报告中记录的canonical路径、package hash和运行时拓扑。出现以下任一情况，必须立即把该单元退回`pending`，不得沿用旧PASS：

- 验收后又修改主文件、references、scripts或templates。
- canonical路径迁移、default/shared/Profile拓扑变化。
- 实时只读事实推翻Skill中的仓库、分支、SSH alias、服务或数据假设。
- 报告hash与当前文件不一致，或运行时可见性变化。

处理顺序：记录失效原因 → 更新队列状态 → 按当前canonical完整回读和重审 → 重新生成hash与运行时证据 → 再入账。不能只刷新显示字段或手工改PASS。

### 用户要求停止或余额不足

用户明确要求“完成当前Skill后停止”、余额不足或停止指令时，覆盖“自动排空队列”规则：

1. 不再启动新单元或新子Agent。
2. 只完成当时正在修改的**一个逻辑Skill单元**，包括附件、回读、12维重审、运行时验证和结果入账。
3. 尚未完成完整验收的其他单元保持`pending`；即使已发生部分修改也不能记为completed，必须在交付中披露。
4. 写回队列，使`completed + pending = total`，保存结果和hash后停止。
5. 自动调度器、standing-goal续跑提示、后台完成通知都不构成恢复授权；不得因这类提示继续取下一单元。只有用户本人在停止之后重新明确说“继续/恢复全库治理”，才恢复排空队列。
6. 最终明确“当前单元完成，全库未完成”，不得用批次或Phase包装成继续执行的请求。

## 6. 全库完成门禁

只有以下条件全部成立才能说“全部完成”：

- 队列中没有 pending/running/failed 单元。
- 所有真实严格 FAIL 为 0。
- 所有 WARN 已修复或有用户明确接受的保留理由。
- 静态结构、引用、frontmatter检查通过。
- 每个相关 Profile 的运行时 Skill 清单验证通过。
- 最终结果基于修改后的全量重跑，不继承修改前评级。

如果后台仍在处理，只报告准确进度和证据路径；不得用“条件通过”或“审计已完成”替代治理完成。