# batch-002-group-3 审核实践手记

来源：2026-07-20 对 3 个自建 Skill 的 Skill Doctor 审核、直接优化、回读复审和结构化结果输出。

## 1. 运行时可见性必须按实际 Profile 分别验证

- `maishi-quote-track` 部署在 `work-web` Profile。
- `maishi-web-app`、`simon-console-maintenance` 部署在 `default` Profile。
- 只在当前 Profile 跑 `hermes skills list` 会漏掉另一个 Profile 的 Skill。
- **做法**：对每个实际部署 Profile 执行 `hermes -p <profile> skills list --enabled-only | grep <skill-name>`，并记录到结果文件的 `verification_evidence.runtime_visible`。

## 2. 优化后必须记录 before/after 量化指标

- 本次优化导致：
  - `maishi-quote-track`：192 行 / 6,501 字节
  - `maishi-web-app`：176 行 / 5,741 字节（从 262 行精简）
  - `simon-console-maintenance`：245 行 / 9,019 字节（从 304 行精简）
- 任何超过 10% 行数/字节变化的优化，必须记录 before/after 行数、字节数和 SHA-256，否则无法证明知识未丢失。
- 如果减少超过 30%，还必须提供删改章节映射、迁移到 references 的目标路径和引用存在性证据。

## 3. references/ 链接存在性要逐个文件验证

- 本次优化后，三个 Skill 的 references 均存在，但机械扫描可能误把反引号中的 `references/xxx.md` 当成 broken reference。
- 正确做法：先读上下文判断是引用还是示例，再用 `skill_view(name, file_path)` 或 `search_files` 确认物理文件存在。

## 4. 结构化结果文件推荐路径

- 写入 `~/.hermes/reports/skill-doctor-full-remediation-YYYYMMDD/batch-XXX-result.json`。
- 每条记录至少包含：
  - `name`、`path`、`files_changed`
  - `before_findings`（12 维 + fail/warn 计数）
  - `after_verdict`（12 维 + fail/warn 计数）
  - `verification_evidence`：readback、frontmatter、fences、references、runtime_visible、sha256、lines、bytes

## 5. Skill 瘦身时保持知识不丢失

- `simon-console-maintenance` 把 Mobile/PWA、Auth 等长段落迁移到已有 references，并用 `Topic-Specific Guides` 索引。
- 不能为瘦身而删除专有知识；只能把详细案例、历史、协议说明移出主文件，并在主文件保留入口。
