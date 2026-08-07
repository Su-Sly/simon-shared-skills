# Markdown 静态审计与增量基线陷阱

用于批量审计 Skill 库时，避免把扫描线索误判为硬错误，或把展示字段漂移误判为内容变化。

## 1. Markdown 链接分层

### 硬错误候选

仅把 fenced code 和 inline code 之外的真实 Markdown 相对链接视为当前包附件：

```markdown
[说明](references/api.md)
```

解析后若当前 Skill 包内不存在，可记为 `broken_relative_reference` error。

### 只作为语义线索

反引号路径不能直接判当前包断链：

```markdown
`references/api.md`
`scripts/run_tests.sh`
```

它可能指向：

- 相邻 Skill 的 reference；
- 被维护项目仓库内的脚本；
- Hermes Agent 源码仓库；
- 命令中的相对工作目录。

必须读取所在句上下文，再递归搜索真实目标。确认正文声明“当前 Skill 包内附件”且目标不存在，才修正文档。

## 2. Inline code 清洗不得跨行

错误写法：

```python
re.sub(r'`[^`]*`', '', text)
```

`[^`]` 会匹配换行。某行出现奇数个反引号时，正则可能跨多行重新配对，吞掉正文并把后续示例链接暴露成真实链接。

正确的最低限度写法：

```python
re.sub(r'`[^`\n]*`', '', text)
```

更复杂 Markdown 应使用逐行状态机或 Markdown parser，不用跨全文的贪婪正则模拟语法。

### 必测 fixture

扫描器修改后至少验证：

1. 真实缺失链接会报错；
2. `` `[x](references/a.md)` `` 示例不报错；
3. fenced code 内链接不报错；
4. 某行孤立反引号不会污染下一行；
5. URL、mail、anchor、绝对路径不按包内附件处理；
6. 反引号中的命令参数不会被并入路径 token。

## 3. 增量继承按物理内容，不按展示标签

比较旧、新 manifest 时，不能把 `profile`、分类名、展示路径标签直接纳入内容变化签名。拓扑构建器可能把同一共享包从 `default/shared` 改标为 `shared`，文件完全没变却导致全库假变化。

可靠签名应基于：

- 解析后的物理 `skill_md` 路径；
- 包内文件相对路径；
- 每个文件的 SHA-256。

不要把 `__pycache__`、`.pyc`、审计报告、临时文件、备份目录计入 Skill 内容签名。

若签名未变，可继承旧语义结果；若变更，使用 remediation overlay 或定向重审，并记录继承数与重审数。

## 4. 语义结果合同必须锁定

接收子 Agent 批次结果时同时校验：

- 单元集合完整且无重复；
- `dimension_id` 恰好为 1–12；
- 每个 ID 对应原始维度名与判据；
- verdict 公式与当前审计合同一致；
- evidence 指向实际文件和当前内容；
- 输入 hash 与产物 hash 可回溯。

尤其不能把第10维“简洁性”替换成“可维护性、版本或 freshness”，也不能在最终合并时临时更换 verdict 公式。发现漂移后应拒收该维度并按原定义重评，不能只改显示名称。

## 5. 完成门禁

最终报告前从零重跑：

1. manifest；
2. Markdown/fence/YAML/语法/secret 静态检查；
3. 当前变化集合计算；
4. 语义基线合并与公式复算；
5. runtime 验证。

报告必须分开呈现：

- 静态 hard error；
- 严格内容质量 verdict；
- 运行影响；
- 本轮新增问题与既有内容债。

不能用“变化批次只剩两个 FAIL”代替117单元全库结论，也不能把严格内容 FAIL 描述成运行故障。
