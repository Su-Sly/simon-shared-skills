# 审计证据与验证闭环

## 1. 证据分级

自动化结果先归类，再定级：

- **事实证据**：完整文件hash、真实命令退出码、API/数据库回读、运行时解析路径。
- **结构线索**：正则、关键词、CLI列表、字符串计数、启发式评分。
- **自报**：Agent/脚本声称PASS、completed或已验证。

结构线索必须人工结合上下文；自报必须由独立证据复核。

## 2. Markdown与路径

- 真实Markdown相对链接按当前文件目录解析，不存在是硬错误。
- fenced/inline code里的链接是示例，不作为依赖。
- 反引号路径只是线索，可能属于其他Skill或目标仓库。
- `skill_view.linked_files`不是完整资产清单；用递归文件清单复核。
- `read_file`的truncated/hint/省略号表示输出分页，不代表源文件损坏。

重写长文件前记录行数、字节和SHA-256。减少>30%时必须有章节映射、迁移目标、引用存在和知识保全证据，否则回滚。

## 3. 凭据线索

- 先排除低熵占位符、测试fixture、`[REDACTED]`、环境变量和协议scheme。
- 只遮蔽secret值，不破坏`Bearer`、`Authorization`等协议常量。
- 修改可执行代码后，用假token + no-network fixture验证最终header和解析。
- 不在报告、命令参数或日志复述真实secret。

## 4. Verification Pattern

### `execution_verification`

必须有：

1. Action：做了什么改变。
2. Verification Target：验证哪个对象。
3. Verification Method：用什么命令/回读/API/日志。
4. Success Criteria：什么结果代表成功。
5. Completion Rule：未通过不得报告完成。

### `quality_gate`

写作、设计、转换等产物定义格式、内容和质量checklist；不伪造外部状态验证。

### `not_applicable`

纯参考知识不产生待验收结果，可无独立验证步骤，但评分证据要说明不适用原因。

## 5. 完整性

正确性与完整性分开：已输出内容真实，不代表输入已完整遍历。按任务选择：

- 长文：总行数/章节、分段起止、首中尾哨兵、最后一段已读取。
- 批量：冻结expected集合，验证`expected = completed ∪ failed ∪ skipped`。
- 多文件：source→target映射、集合差、hash和内容抽样。
- 分页：页码/游标/数量，到达空页、`next_cursor=null`或官方总数终点。
- 搜索：无法证明穷尽时写“在已检索范围内”并披露范围。

无命中不等于未读取；固定尾部比例不是普适阈值。

## 6. 评分器与脚本自验

- 用已知PASS和已知FAIL样本各跑一次；修改评分器后重跑。
- 首次FAIL先区分被测对象、评分脚本、工作目录/环境错误。
- 脚本应有参数、退出码、日志、正常/失败/边界fixture和结构化输出。
- 包结构检查运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_audit_skill_package.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/audit_skill_package.py . --format json
```

该脚本是只读结构审计器；语义冲突、安全授权和业务完整性仍由Agent复核。

## 7. 官方文档

对象背后有维护契约的权威方，就锚定官方文档链接并记录查证日期。审计时验证链接可达、关键命令/字段与最新版一致；自建内部流程没有权威文档时不硬塞。

Hermes Agent官方文档（核对2026-08-08）：https://hermes-agent.nousresearch.com/docs