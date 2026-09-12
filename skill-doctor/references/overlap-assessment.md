# Overlap assessment (v3.9.0) — 第 5 维强制子审计执行细则

检测被审 Skill 与库内其他 Skill 的**实证重合**，抓两类问题：越权正文（写了别的 canonical Skill 的领地）、过期指令（引用了他 Skill 已废弃的事实）。与 split_assessment（第 1 维）互补：一个向内看合同边界，一个向外看库一致性。

## 机械层：`scripts/check_cross_skill_overlap.py`

身份 token（脚本名、`ENV_VAR` 风格变量、三段以上 config 键、有意义路径）双向 grep，只输出计数矩阵，零 LLM token：

```bash
python3 scripts/check_cross_skill_overlap.py <目标Skill根目录> --lib ~/.hermes/skills
```

- **forward**（他 Skill 的 token 出现在目标正文）：越权/过期风险
- **reverse**（目标的 token 出现在他 Skill）：重复/漂移风险

批量全库约 3 分钟（一次落盘 JSON，批量审核复用，勿逐个重扫）。

降噪内置：`.md` 文件名、浅路径（无 ≥2 个有意义段）、stdlib 惯用式（`os.environ.get` 等）、`API_KEY` 类通用词自动剔除。调阈值改脚本头 `THRESHOLD`，不要绕过脚本手搓 grep——历史教训：Agent 全库 grep 一次 60+ 假阳性（2026-09-12 实测），脚本同数据压到 ≤6。

## 语义层：审计四步（硬上限）

1. 必跑一次脚本（单 Skill 审计）；批量审计用 batch JSON，不重跑。
2. 每个候选 peer 只读命中行 ±10 行（`search_files` context 参数），**候选 >3 个时按 token 区分度取前 3**，其余记 `UNREVIEWED_LOW_SIGNAL`。
3. 逐候选裁决（固定五选一，附路径+行号证据）：
   - `CANONICAL_HERE` — 重合知识本 Skill 是权威，他处应留指针
   - `CANONICAL_THERE_ADD_ROUTE` — 权威在他 Skill，本 Skill 改为路由/指针
   - `DUPLICATE_MIGRATE` — 双方都有正文，需迁移动议（迁移动议≠实施授权）
   - `STALE_INSTRUCTION` — 他 Skill 含过期事实，列入整改项
   - `FALSE_POSITIVE` — 附理由
4. 完成门禁：无脚本运行证据、`overlap_assessment` 块缺失、或存在已读上下文但未裁决的候选 → 审计不得报完成。

## 固定输出schema

`overlap_assessment`必须包含：`script_evidence`、`forward_candidates`、`reverse_candidates`、`verdicts`（逐候选裁决及路径+行号证据）、`unreviewed_low_signal`、`rationale`。这是从主入口迁来的原合同，不放宽字段、枚举或完成门禁；不能用自然语言摘要替代机器字段。

## Token 成本基准

单 Skill 审计增量 <2k token（脚本矩阵 <100 行 + 最多 3 候选 ×60 行 + 裁决 ~15 行）。超预算说明你在读不该读的全文——回到 ±10 行窗口。

## 校准锚点（2026-09-12 cron-management 案例）

- 瘦身**前**版本：reverse 抓到 `TAVILY_API_KEY`/`web-search-watchdog.py` 写死在 cron-management 正文（STALE_INSTRUCTION + 越权），forward 抓到 `hermes-web-search-operations`、`external-credential-health` 双向实证。
- 瘦身**后**版本：canonical 信号仍在（reference 中的 watchdog 名），但 TAVILY 过期项消失——脚本可回归验证整改效果。
- 阴性组（ascii-art/pixel-art/humanizer）：0 候选。

## 边界

- 官方/上游 Skill、fork：候选照常产出，裁决只记录不改（只审不改契约优先）。
- `FALSE_POSITIVE` 不需要整改，但理由必须具体（哪个 token 为何无意义）。
- 本子审计不改 12 维结构、不新增维度；批量模式下每个 Skill 的裁决仍须独立得出，禁止复制模板结论。
