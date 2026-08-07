# Phase 5 Batch 3 手工语义审核门禁笔记

场景：一次 `phase5-semantic-delta` 批量审核，共 11 个 skill 单元，需按 12 维度逐项给出 ✅/⚠️/❌，并写入合规 JSON。

## 输出格式

```json
{
  "schema_version": 1,
  "batch": 3,
  "input_sha256": "<input manifest sha256>",
  "units": [ { unit_id, path, verdict, dimensions: [...12] } ],
  "summary": { unit_count, verdict_counts: { PASS, WARN, FAIL } }
}
```

## Verdict 公式（必须严格复用）

- 任一维度为 ❌ → `FAIL`
- 否则任一维度为 ⚠️ → `WARN`
- 否则 → `PASS`

**手工编辑 verdict 时必须同步重算 summary 计数。**

## 实测陷阱

1. `production-webapp-maintenance` 维度 4（负触发）原本评 ⚠️，但 `verdict` 被写成了 `PASS`。
   - 第一次自校验：机器按公式重算，发现不一致，校验失败。
   - 修复：将 `verdict` 改为 `WARN`。
2. 改完 verdict 后未改 `summary.verdict_counts`。
   - 第二次自校验：机器期望 PASS 6 / WARN 5 / FAIL 0，但实际是 PASS 7 / WARN 4 / FAIL 0。
   - 修复：手动将 summary 同步为 PASS 6 / WARN 5 / FAIL 0。
3. 最终 SHA256 才稳定为 `24c21aba8248d04e5dfa14fcc4eaa146ba5f630e44fe349e164b61aa86bd3c2d`。

## 推荐验证脚本

```python
import json, hashlib, sys
p = '<result.json>'
with open(p, 'rb') as f:
    raw = f.read()
data = json.loads(raw)

# basic structure
assert data['schema_version'] == 1
assert data['batch'] == 3
assert len(data['units']) == 11
for u in data['units']:
    assert len(u['dimensions']) == 12
    assert [d['dimension_id'] for d in u['dimensions']] == list(range(1,13))
    # verdict formula
    statuses = [d['status'] for d in u['dimensions']]
    exp = 'FAIL' if '❌' in statuses else ('WARN' if '⚠️' in statuses else 'PASS')
    assert u['verdict'] == exp, f"{u['unit_id']}: {u['verdict']} vs {exp}"

vc = data['summary']['verdict_counts']
assert vc['PASS'] + vc['WARN'] + vc['FAIL'] == 11
# also assert vc matches recomputed counts
from collections import Counter
computed = Counter(u['verdict'] for u in data['units'])
assert vc['PASS'] == computed['PASS']
assert vc['WARN'] == computed['WARN']
assert vc['FAIL'] == computed['FAIL']

print('sha256:', hashlib.sha256(raw).hexdigest())
print('OK')
```

## 人工审核时的 checklist

- [ ] 写完 JSON 后先机器校验，不要直接交付
- [ ] 校验失败时优先按公式重算 verdict，而不是手动覆盖
- [ ] 改 verdict 后必须同步 `summary.verdict_counts`
- [ ] evidence 不能为空，且必须引用原文行号或片段
- [ ] 最终输出文件路径 + SHA256 + 统计

## 何时触发此模式

- 用户要求“人工完成第 N 批 X 个单元并写入合规 JSON”
- 批量语义审核结果需要持久化为可验证文件
- 需要避免手工编辑 verdict 与 summary 计数的漂移
