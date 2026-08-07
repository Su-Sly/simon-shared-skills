# Skill Library Baseline Audit

用于一次性审计整套本地维护 Skill 库；不要把物理文件数直接当审计单元数。

## 1. Scope by provenance

先递归发现所有 Profile，再分类：

1. 官方/Hub 原样副本：与官方或安装源 `name + SKILL.md hash` 一致，排除修改范围。
2. 本地维护 canonical：按逻辑 Skill 分组，一个 canonical 算一个审计单元。
3. 官方衍生分叉：hash 已偏离上游，每个真实分叉单独审计。
4. 归档、备份、缓存、`.restore-backups`：不属于 active scope。
5. Profile 特定 Skill：只有业务边界真实不同才保留独立单元。

审计总数 = 本地维护逻辑 canonical 数 + 真实维护分叉数；不是磁盘上的 SKILL.md 数。

### Manifest contract

manifest 在冻结范围时就要保存来源证据，避免 Phase 1 再猜字段或重新发现上游：

- 顶层：`schema_version`、`generated_at`、`units_count`、分类计数。
- 每个单元：`unit_id`、`name`、`kind`、`paths[]`。
- 每个物理包：`profile`、`skill_md`、`package_dir`、Skill/bundle hash、文件清单。
- 官方衍生分叉额外保存：`upstream_path`、`upstream_skill_sha256`、`upstream_bundle_sha256`；上游不可定位时显式写 `upstream_status: unresolved`，不能省略字段。
- canonical 重复组保存全部物理路径，不要只留推荐路径。

消费 manifest 前先验证 `schema_version` 和真实字段位置，不要按上一版脚本假设字段。若必须补查上游，递归覆盖 default 安装根、源码根（如 `~/.hermes/hermes-agent/skills/`）、各 Profile 与 external dirs；多候选时记录歧义，不静默选择。

## 2. Execution order

1. **Stabilize partial rollouts**：若同一治理规则存在 V1/V2 混用，先备份并恢复一致，再开始基线审核。
2. **Topology/drift**：先确定 canonical、重复组和官方分叉，避免分别优化重复副本。
3. **Static checks**：YAML、fence、references、secret scan、行数、重复章节、过期路径、日志与验证关键词。
4. **12-dimension semantic audit**：每批 8–12 个，只读子 Agent并行；输入使用固定 manifest。
5. **Main-agent review barrier**：全部异步结果返回并复核后才能发布语义结论。
6. **Risk-ranked changes**：P0 生产/配置/部署/服务器/cron/邮件/财务/安全；P1 高频业务；P2 低风险内容工具。
7. **Per-batch confirmation and modification**：诊断后确认，5–10 个同主题 Skill 一批；备份、修改、重审、运行时验证。
8. **Full regression**：重新生成拓扑，不沿用修改前计数。

## 3. Gate template requirements

统一 Freshness/Completion Gate 至少要包含：

- **Trigger**：谁在什么事件后、交付前何时执行。
- **Decision**：哪些持久变化必须更新，哪些无需更新。
- **Action**：对照实际运行证据更新 SKILL.md/references。
- **Audit**：内容变化后运行 skill-doctor；修到本次新增 ⚠️/❌ 为 0。
- **Readback**：当前 Profile 用 `skill_view`；跨 Profile 用完整文件回读 + 对应 Profile runtime discovery。
- **Evidence**：交付时给固定的 updated/no-update 证据行。
- **Termination**：门禁内的 Skill 文档修改不重新触发门禁；既有非阻塞警告不造成无限循环。

## 4. Async audit pitfall

静态检查通过不等于 12 维语义审核通过。后台审核尚未完成时不得提前交付“全部 PASS”。异步结果返回后，如果推翻早先判断，应直接更正，并把误判与真实问题分开处理。

## 5. Static findings are leads, not verdicts

静态扫描必须输出 raw finding，之后由主 Agent 标成 confirmed / false positive / semantic review pending。常见误判：

- 相对路径可能是示例或全局脚本，不一定是包内断链；
- Shell 脚本没有执行位，但若始终用 `bash script.sh` 调用，不一定故障；
- 重复标题和长文件只能作为上下文成本线索，不能自动重写；
- fence 必须按逐行状态机判断，不能简单统计正文中 ` ``` ` 字符串次数。

执行时必须重扫并核对旧计划数字。现场数据与计划不一致时，以现场证据修正 manifest 和计划，不能为了匹配旧数字硬凑。

## 6. Credential leak handling

发现疑似 Token/Key 时：

1. 报告只记类型、路径、行号，不回显值。
2. 不调用外部 API 测试有效性。
3. 本地判断重复值时只输出数量和是否相同。
4. Git 历史搜索使用凭据类型正则，不把真实值放入命令行或报告。
5. 区分工作树未提交、已进本地提交、已进 remote-tracking refs；未 fetch 时明确 remote-tracking 不是远端实时证明。
6. 若泄露位于尚未 push 的本地提交，禁止直接 push：先轮换凭据、替换示例、重写本地提交、复查历史。追加“删除 Token”提交不能清除旧历史。

## 7. Uniform batch output contract

子 Agent 的自报“已按12维审核”不能作为验收。派发时固定并逐项验证以下合同：

1. 维度必须严格等于主 SKILL.md 的原始12维，名称、顺序、数量都一致；不得用 YAML、依赖、Freshness Gate 等自创维度替代。
2. 每维都有 `status`（✅/⚠️/❌）和原文行号或片段证据；空证据直接判产物无效。
3. 统一 verdict：任一❌或至少3个⚠️=`FAIL`；1–2个⚠️且无❌=`WARN`；全✅=`PASS`。
4. `risk` 表示修复优先级，不等于 verdict；不能因为 FAIL 自动写 P0。
5. `findings` 只列⚠️/❌，且不得回显凭据值。
6. 每批输出固定 JSON schema、唯一 `unit_id`、输入单元数和文件 SHA256。

主 Agent 合并前必须机器校验：

- 报告文件 hash 与子 Agent 自报一致；
- `reported unit_id set == input unit_id set`；
- 批内无重复、批间无重叠、全库无漏项；
- 每单元恰好12维且 ID/顺序正确；
- verdict 按状态重新计算，最终统计不采用子 Agent 自报；
- evidence 非空，findings 不含密钥正文；
- 静态扫描的风险等级与语义 verdict 分列，不互相覆盖。

若某批使用了另一套维度、schema 不兼容或统计与明细不一致：保留原产物并标记 `invalid`，只重跑该批；不得为了赶进度把它拼进总报告。

## 8. Full-library completion evidence

- manifest 与重新扫描一致；
- 修改前归档可打开，且覆盖 manifest 的全部物理包；记录大小、成员数和 SHA256；
- 官方原样 Skill 零误改；
- 每个重复组有 canonical 结论；
- 每个审计单元有证据化诊断；
- 子 Agent 产物由主 Agent读回、核数并校验后才算完成；
- 修改批次新增问题为 0；
- 所有目标 Profile 配置与运行时发现通过；
- 最终报告明确区分“已修复”“已确认问题”“静态线索”和“未完成”；
- 有备份、回读和回滚路径。

## 9. Phase 5 scope drift and orphan-secret handling

A frozen manifest is the audit contract, not proof that the active tree is unchanged. During final regression:

1. Re-hash every manifest unit from the current filesystem and separately scan for active packages created after the freeze.
2. If a new locally maintained Skill is active, add it as a new audit unit and update all counts; do not force the result back to the old total.
3. Scan the **entire active Skill roots**, not only manifest package directories, for credential patterns. Orphan directories/files without `SKILL.md` can still contain live secrets and are invisible to a package-only audit.
4. Keep active findings separate from backups, archives, reports, and session history. Backup hits are real exposure inventory but do not equal active runtime exposure.
5. Never trust a Skill's statement that a separate canonical data file exists. Verify destination existence and compare content/key-set hashes before removing or overwriting a misplaced copy.
6. If the misplaced file is the only complete copy, preserve it and obtain confirmation before moving/deleting it. A security cleanup must not destroy the only business data source.
7. Secret redaction can corrupt executable code. After any scrub, inspect changed lines and run **side-effect-free** syntax checks: Python用内存 `compile(source, path, "exec")` 或 `ast.parse`，Shell用 `bash -n`；不要在活跃Skill树内调用会写入 `__pycache__` 的 `py_compile`。随后重跑整个活跃树密钥扫描，不只扫被编辑包。
8. Reports must not emit credential values. Record type, path, line/count, entropy/placeholder classification, and non-reversible hash prefixes only.

## 10. Incremental semantic re-audit by package hash

Phase 5不必把字节完全未变的单元再次交给LLM重审，但继承旧证据必须满足严格条件：

1. 以 `unit_id + package_dir + files[].path + files[].sha256` 比较旧manifest与当前manifest；不能只比 `SKILL.md`，references/scripts变化也会改变语义或运行行为。
2. 先检查旧/新manifest的schema与字段层级。`bundle_sha256`可能位于 `paths[]`，旧manifest也可能没有该字段；字段不存在时不得把两个 `None` 当成哈希相等。
3. 旧manifest无bundle hash时，使用其已保存的 `files[]` 按当前算法重新计算；算法必须明确固定（排序、分隔符、路径编码），否则不同算法的hash不能直接比较。
4. 只有逐文件集合与SHA完全一致的单元可以继承旧12维证据；任一文件新增、删除、变化，或新加入审计范围的单元，都必须重新语义审核。
5. 报告分别记录 `inherited_unchanged_units` 与 `rescored_changed_or_new_units`，并保留manifest hash，不能把增量审核表述成“117个全部重新人工阅读”。
6. 如果旧语义基线本身被判无效，hash未变也不能继承，必须重审。

## 11. Human-facing report gate

全库审计最终交付优先使用移动友好 HTML，并同时保留 JSON/Markdown 机器证据。报告必须：

1. **分离两条轴**：内容质量 `PASS/WARN/FAIL` 与运行影响 `P0/P1/P2` 分开展示；显式说明严格 `FAIL` 不等于运行故障。
2. **先放阻塞项**：凭据泄露、禁止 push、生产风险等必须出现在首屏，不埋在附录。
3. **范围可核对**：显示逻辑单元、物理包、排除项、漏计修正、Profile 验证数。
4. **可下钻**：提供12维热力图、全部单元表格及按名称/tier/verdict筛选。
5. **证据可复现**：列出备份、源报告 hash、manifest、统一基线和生成器路径；不回显密钥正文。
6. **结构验收**：程序检查单元行数、维度数、关键警告、HTML闭合及敏感凭据正则零命中。
7. **视觉验收**：用可用浏览器检查首屏和响应式布局；若无浏览器且不得擅自安装，可用系统原生 HTML/Quick Look 渲染生成截图，再做视觉检查。视觉验收不能替代结构验收。
8. **交付方式**：消息平台直接附加 HTML 文件，不让用户自行查本机路径。

## 12. Final merge, regression accounting, and acceptance

增量审计的最终合并不是简单拼接批次结果。固定顺序：

1. 从不可变旧语义基线开始；仅逐文件集合与SHA完全一致的单元允许继承。
2. changed/new 单元覆盖为本轮人工批次结果。
3. 后续定向重评分覆盖较旧批次结果。
4. 批次完成后又修改过的单元必须加主 Agent `manual overlay` 或重新审核；不能沿用修改前证据。
5. 最后统一校验 `dimension_id → dimension`、12维数量/顺序、证据非空，并按锁定公式重新计算 verdict。

### 回退核算

对所有内容变化单元输出 `before → after`，至少分成：`improved / same / regressed / new`。任何 `regressed` 都要逐项复核：

- 若确实改坏，先修复并重跑；
- 若是旧审核漏判或新批次口径更严格，写成“assessment correction”，但仍按当前合同处理真实缺口；
- 不得用全库总数改善掩盖单个回退；最终基线的新增语义回退应为0，除非报告明确接受该债务。

### 验收必须拆轴

最终JSON至少独立给出：

- `audit_execution`：拓扑、schema、静态、语义合并和报告构建是否完成；
- `runtime_integrity`：Profile discovery/config、备份、retired path、secret scan、触发模拟是否通过；
- `content_quality`：严格12维是否仍有FAIL；
- `overall`：存在内容债或未授权端到端验证时用 `CONDITIONAL_PASS`，不能写成无条件PASS。

`review_priority=P0`仍不是运行阻塞。运行P0阻塞要由硬门失败定义，例如真实凭据、语法/YAML/链接硬错误、Profile不可见、配置检查失败、触发冲突、备份损坏或retired path仍被引用。

### 构建器与基线锁定

- 消费JSON前读取并验证真实顶层keys；CLI打印的摘要字段不保证存在于文件中的`summary`对象，禁止按上一版脚本或终端输出猜schema。
- 锁定基线保存：manifest/static/semantic/runtime/trigger hash、每单元当前内容hash、verdict公式、硬门结果、排除项和增量继承规则。
- 报告、acceptance、baseline、checksums存在相互引用时避免hash循环：先写证据和baseline，再写acceptance/HTML，最后生成独立checksums清单。
- 报告生成后同时做JSON解析、HTML结构解析、硬门断言和真实视觉渲染；任一失败先修生成器，再覆盖旧产物。
- 删除缓存、restore backup、升级Profile schema、重启Gateway等仍遵守原授权边界；把未授权项列入排除项，不为“总验收好看”擅自执行。
