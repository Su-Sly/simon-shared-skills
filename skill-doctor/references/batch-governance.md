# 批量审计与全库治理

用于多Skill、跨Profile、委派审计和连续整改。固定使用Skill Doctor当前12维；架构一致性、安全规避、运行时状态是横切字段，不伪装成第13维。

## 1. 冻结输入全集

先递归发现，再分类：

1. default、所有Profile、shared、配置中的`skills.external_dirs`。
2. 官方/Hub原样副本、本地canonical、官方衍生分叉、归档/备份。
3. 以逻辑Skill为单元，保存每个物理包的profile、路径、name、文件清单、SKILL hash和包hash。
4. 同名组保存全部路径和来源，不能只留推荐路径。
5. 正向扫描后，再用中英文职责关键词反向查漏；补漏后从零重跑范围验证。

缺失manifest路径时，换用递归搜索确认迁移/重命名；确实不存在则标missing并继续，不反复读取同一路径。

## 2. 运行时与canonical

- `hermes skills list`的enabled只证明可见，不证明裸名称唯一解析。
- 按frontmatter `name`扫描活动发现范围；备份目录不算活动副本。
- 在目标Profile实际以裸名称加载，记录解析路径。
- 单一流程优先共享canonical；真实业务分叉才保留复制。
- 官方Skill先用Hermes官方diff/reset/update链路，不把optional、seed或归档副本误认成自建canonical。

### 跨Profile授权Checklist

只有用户明确指定目标Profile和修改范围后，才能使用`cross_profile=True`：

- [ ] 目标Profile、文件和动作已列明；
- [ ] 已保存快照、diff和回滚路径；
- [ ] 修改后完整回读并运行该Profile的`config check`/`skills list`；
- [ ] 删除、移动旧副本或归档目录已单独获得数字授权；
- [ ] 未获删除授权时只报告或做可逆归档，不删除。

## 3. Canonical自动化

批量机械步骤必须复用参数化脚本，不按batch复制`audit_batch1.py/audit_batch2.py`：

1. 输入manifest作为参数。
2. 静态脚本输出结构化线索，不直接替代语义评分。
3. 统一维度schema、verdict公式、risk与verdict分离规则。
4. 保存脚本版本/hash、输入hash和产物hash。
5. 已有正确提取结果可复用，不丢弃标准化元数据重做。

Skill包自身结构检查使用`../scripts/audit_skill_package.py`；它只读检查YAML、围栏、链接、维度schema、脚本语法、hash和凭据线索。

## 4. 批量语义审计

- 每个维度证据带路径、行号或片段。
- 每个逻辑Skill必须生成独立`split_assessment`：使用日志证据的来源/窗口/命中/盲区 + 候选职责五场景逻辑推演 + 四选一结构verdict；该结果归入第1维，不新增第13维。
- 批量时可一次检索日志后按Skill和调用去重归档，但不能用统一模板给所有Skill复制同一结论；无日志的单元标`usage_evidence.status=none`。
- 一次审N个Skill时，人读报告只展开⚠️/❌及非`KEEP_SINGLE`的拆分建议；机器结果仍保留完整12维和每单元`split_assessment`。
- ≥3个Skill同维度⚠️时，标为系统性缺口。
- 自动化首轮后从FAIL/WARN随机抽3–5个复核；若某维度≥80%失败，优先怀疑启发式过严。
- 工作流识别动作性标题、祈使bullet、顺序和命令块，不只数编号步骤。
- 静态命中、运行状态`completed`和子Agent自报都只是线索。

## 5. 委派合同

派发时固定：输入单元、原始12维名称、JSON schema、verdict公式、风险字段和输出路径。

### 单单位调用预算

子任务容量必须写进合同，不能只限制命令超时：

- 单 Skill 任务目标不超过38次工具调用；前10次完成冻结、必要读取和before，证据不足记WARN/NOT_TESTED，不无限诊断。
- 第11–18次完成三方hash备份与精准编辑；第19–30次一次性生成after和7件产物；最迟第34次运行validator，剩余调用只修验收错误。
- 三个以上独立读取、hash或JSON处理应合并执行，禁止按文件碎片化调用。
- 预算不足时优先保留未修WARN并完成可验收闭环；只完成诊断、未生成after/产物/validator的worker必须判未完成并从检查点续跑。
- 每次写入必须检查工具返回的`success`、`verified`或`files_modified`；软守卫拦截、空修改、写入失败都必须判未落盘，不能因调用未抛异常而继续。
- 跨Profile写入只在用户已明确授权目标Profile与路径时使用`cross_profile=true`；写后回读现场文件并重算hash，临时文件或内存字符串不能作为落盘证据。

主Agent必须独立核验：

- 输入集合与产物集合相等；
- 每个单元12维恰好齐全且名称正确；
- 每个单元`split_assessment`字段齐全，日志统计可追溯，逻辑推演不是同义反复；
- evidence非空，计数与verdict可重算；
- 产物文件存在、可解析、hash一致；
- worker没有在文字中承认未完成或保留未计数warning；
- 安全、架构、外部系统状态独立复核。

首个worker结果先校准，通过前不补满并发位。无证据大幅删减时，从快照恢复该worker修改的文件。

## 6. 增量与完整性

只有物理包hash完全一致且旧基线合同有效时，才继承旧语义结果。记录：

- inherited、reaudited、new、missing数量；
- expected = completed ∪ failed ∪ explicitly_skipped；
- duplicate、unknown、missing必须为0或有明确解释；
- changed/new全部重审，不能冒充全量人工重读。

## 7. 整改和完成门禁

- 审计完成：范围、证据、报告生成，允许FAIL/WARN。
- 治理完成：授权范围内FAIL全部修复；未接受的WARN列为未完成。
- canonical修改后重新回读、运行包审计脚本并验证运行时。
- 用户要求停止或余额不足时，只验收当前逻辑单元，不由standing-goal恢复授权。
- 最终拆分：`audit_execution`、`runtime_integrity`、`content_quality`、`external_system_status`、`overall`。
- 严格FAIL存在时，不得回答“全库通过”。

## 8. 历史经验

历史批次证明：编号步骤启发式曾造成39/39误判；profile-specific路径可能遮蔽shared canonical；输出schema合法不代表维度语义正确；脚本自报SHA/PASS不能替代父审计。原始批次材料已可逆归档，当前规则以本文件和主SKILL.md为准。