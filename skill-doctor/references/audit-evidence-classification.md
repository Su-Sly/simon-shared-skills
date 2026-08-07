# 审计证据分类与误报门禁

用于 Skill 全库审计、安全扫描、运行时发现和补丁验证。核心原则：**扫描命中是线索，不是结论；验证必须对准语义对象。**

## 1. 凭据正则命中：先分类，再定级

正则匹配到 `ghp_`、`sk-` 等前缀时，不得直接升级为真实泄露或P0。按顺序检查：

1. **上下文**：文档示例、环境变量、脱敏标记、测试fixture，还是实际配置值。
2. **占位符特征**：全 `x`、全 `0`、重复单字符、`...`、`<TOKEN>`、`${ENV_VAR}`、`REDACTED`。
3. **字符分布**：记录后缀长度、唯一字符数、是否全相同；必要时计算 Shannon 熵。
4. **传播边界**：只在排除占位符后，才检查Git历史、远端、备份和运行环境。
5. **处置等级**：只有“非占位符 + 格式可信 + 上下文指向真实配置”时，才建议轮换、阻断push或历史清理。

低熵判断示例：

```python
from collections import Counter
from math import log2

body = token.split('_', 1)[1]
counts = Counter(body)
entropy = -sum((n / len(body)) * log2(n / len(body)) for n in counts.values())
print(len(body), len(counts), entropy)
```

注意：熵只是分类证据，不是“高熵就一定真实”的证明。不得为了验证而调用或测试疑似凭据。

## 2. 运行时发现：防止表格截断假阴性

`skills list` 等CLI可能按终端宽度截断名称。不能因为完整名称未出现在窄表格里，就宣布Skill不可见。

验证顺序：

1. 用宽列或机器可读输出，例如 `COLUMNS=500 hermes skills list`。
2. 同时验证命令退出码和目标名称。
3. 需要时用直接加载/inspect交叉验证。
4. 跨Profile逐一运行，不从default结果推断其他Profile。

“直接加载成功但列表字符串搜索失败”应先怀疑显示截断，而不是立刻改文件或重建索引。

## 3. 结构补丁验证：统计语义块，不统计全文件

目标是字典、注册表或配置块时，只截取对应结构再计数。全文件可能在注释、其他集合、测试常量中出现同名字符串，造成重复项假阳性。

```python
text = path.read_text()
start = text.index('SUPPORTED_DOCUMENT_TYPES = {')
end = text.index('\n}', start)
block = text[start:end]
assert block.count('".html"') == 1
```

幂等补丁至少覆盖三类fixture：

- 目标项全部缺失
- 目标项部分存在
- 目标项已全部存在/上游已内置

每种fixture连续运行两次；第二次内容哈希不变才算幂等。

## 4. 相对路径：Markdown链接与反引号路径分级

路径语法代表不同证据强度：

- `[说明](references/a.md)`：明确声明当前包的相对链接；解析后不存在可判硬错误。
- `` `references/a.md` `` / `` `scripts/run.py` ``：只算线索。它可能是当前包资产，也可能在句子前文指向另一个 Skill，或代表目标项目仓库内的运行时路径。
- `../other-skill/references/a.md`：先解析相邻包并确认其拓扑；不能按当前包直接判断链。

处理顺序：读完整句子 → 识别目标 Skill/仓库 → 搜索真实目标 → 再定级。`skill_view.linked_files` 只用于发现，不是“文件不存在”的充分证据；非 Markdown 资产可能不展示，最终以实际文件搜索为准。

## 5. 安全修补：凭据值与协议常量分离

脱敏只处理凭据值，不改协议语法。以下内容不是密钥：

- `Authorization: Bearer `
- `Authorization: Zoho-oauthtoken `
- 环境变量名、header名、URL路径

禁止把 scheme 替换成 `***` 后仅靠语法检查交付——脚本会合法运行但请求必然失败。修补可执行代码后，用假 token 和 no-network fixture/monkeypatch 捕获最终请求参数，断言 header scheme、JSON序列化和响应解析均正确；测试不得调用真实凭据或外部API。

## 6. 批次语义 schema：ID与名称必须同时锁定

仅确认维度ID为1–12不够。必须校验固定映射，特别是：

- 7 = 工作流
- 9 = 质量标准与验证闭环
- 10 = 简洁性
- 11 = 硬规则 vs Checklist
- 12 = 日志与可观测性

若子Agent把第10维改成“可维护性/版本/freshness”，即使JSON、数量和verdict公式都合法，结果仍无效。主Agent应拒收漂移维度并按原始判据重评，不能只改标签。

## 7. Git与基线边界

- 混合脏工作树中，不把整个 `git diff` 归因于当前Phase。
- 优先用审计前归档、逐文件哈希和明确路径划分本次变更。
- 没有真实凭据或错误提交证据时，不做 `reset --hard`、历史重写或额外“清理提交”。
- 全库基线保持不可变；局部修复写成 remediation overlay。
- 只重审了少数Skill时，只更新这些单元的定向Verdict，不重算或改写全库统计。

## 8. 报告措辞

必须分开写：

- **运行/安全风险是否消除**
- **严格内容质量Verdict是否通过**
- **静态/fixture验证是否通过**
- **运行中服务是否已加载新代码**
- **端到端场景是否实际复现**

静态通过不等于运行时已加载；局部P0修复通过也不等于整个Skill达到12维PASS。