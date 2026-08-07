# 返工审计报告：只读重审与替换流程

用于 `skill-doctor` 12 维批量审计报告被标记 invalid / 需要返工时，重新生成 schema 对齐的 JSON 与 Markdown 报告并自验证。

## 触发条件

- 用户说："重新完成批次 X 的 N 个 Skill 只读审核"
- 用户说："替换无效报告并自验证"
- 既有报告文件被判定为 schema 不一致、维度数错误、verdict 公式错或缺失 SHA256

## 与常规审计的区别

| 常规审计 | 返工审计 |
| --- | --- |
| 发现缺陷、列出建议 | 必须产出可直接替换旧报告的新文件 |
| 可只输出摘要 | 必须输出 schema 对齐的 JSON + Markdown |
| 不一定重新读源文件 | 必须重新读取全部 `SKILL.md` 并基于当前内容评分 |
| 可人工交付 | 必须自验证并给出 SHA256 |

## 工作流

1. **定位批次源文件**
   - 读取 `~/.hermes/reports/skill-audit-<YYYYMMDD>/phase3-batch-<N>.json`
   - 确认 `units` 数组、每个 unit 的 `paths[0].skill_md`

2. **重新加载所有 SKILL.md**
   - 使用 `read_file` 逐条读取；每个 unit 只读其 canonical `SKILL.md`
   - 不要修改任何 Skill 文件或技能逻辑

3. **按 12 维评分**
   - 每维必须给出 ✅/⚠️/❌ 并附具体证据（原文或行号）
   - 审计必须是只读的

4. **构建输出结构**
   - JSON schema：
     ```json
     {
       "batch": N,
       "audit_date": "ISO8601",
       "units_count": 42,
       "audit_framework": "skill-doctor 12-dimension read-only",
       "units": [ { ... } ]
     }
     ```
   - 每个 unit 必须包含：`unit_id`、`name`、`kind`、`canonical_profile`、`canonical_path`、`paths`、`drift`、`verdict`、`risk`、`dimension_status`（12 项）、`findings`、`strengths`、`phase4_recommendations`、`summary`

5. **Verdict 公式**
   - `FAIL`：任一维度 ❌，或 ⚠️ ≥ 3
   - `WARN`：无 ❌ 且 1–2 个 ⚠️
   - `PASS`：全部 ✅

6. **运行影响等级（与内容 verdict 分离）**
   - `P0/P1/P2` 只表示运行影响和修复优先级，不能从 `FAIL/WARN/PASS` 自动推导。
   - `P0`：生产配置、凭据、安全、财务、邮件发送、服务器、Gateway、部署、cron 等高影响路径。
   - `P1`：高频业务流程或可恢复的外部状态变化。
   - `P2`：纯内容、创作、转换或低影响辅助能力。
   - 严格内容 `FAIL` 不等于运行故障；低风险内容 Skill 可以 `FAIL + P2`，高风险运维 Skill 也可以 `PASS + P0`。

7. **生成 Markdown 摘要**
   - 含总体统计、unit 汇总表、按 unit 列出 findings

8. **主 Agent验收（不能采用子 Agent自报）**
   - 先确认规定输出文件真实存在并可解析；任务状态显示 `completed` 但文件不存在，整批判 `invalid`。
   - 子 Agent摘要若自述“只读了部分文件”“尚未完成人工复核”“因工具调用上限停止”，即使状态为 `completed` 也判 `invalid`。
   - 输出 `unit_id` 集合必须与输入完全一致，不能缺项、重复或混入其他批次。
   - 每单元必须恰好 12 维，`dimension_id` 是整数 `1..12` 且顺序正确。
   - evidence 必须包含源路径/行号和能支持判断的内容；只有行数、description长度、通用套话不算语义证据。
   - 批量启发式出现异常同质结论（例如整批39/39 FAIL）时，抽样3–5个源文件人工复核；确认是格式启发式误判后，废弃整批，不做局部粉饰。
   - 每个 `verdict` 按维度状态重新计算，不采用summary自报统计。
   - JSON可解析、文件SHA256由主 Agent对实际文件重新计算，与子 Agent自报不一致则标记无效。

9. **计算 SHA256**
   - 对 JSON 报告和 Markdown 摘要分别计算 SHA256
   - 在最终回复中报告两个 hash

## 输出命名

- JSON：`phase3-agent-<N>.json`
- Markdown：`phase3-agent-<N>.md`
- 写入目录与旧报告相同：`~/.hermes/reports/skill-audit-<YYYYMMDD>/`

## 禁止事项

- 不修改被审 Skill 的 SKILL.md
- 不沿用旧报告中的维度评分，必须重新基于当前文件内容评分
- 不省略自验证和 SHA256
- 不将静态 YAML/fence/引用检查冒充为语义 12 维审核
