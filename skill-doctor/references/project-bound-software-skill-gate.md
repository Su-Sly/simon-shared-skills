# 项目绑定型软件维护 Skill 门禁

## 适用范围

仅当 Skill 对应的对象同时满足以下三项时启用：

1. 有可独立识别的源码资产，而不是仅供Skill调用的小脚本或wrapper；
2. 有独立维护生命周期，会持续开发、升级、修复或由不同Agent接管；
3. 有独立发布/部署/生产边界，例如网站、App、业务系统或长期运行服务。

脚本、CLI、SQLite、日志、本地Git、代码路径、域名任一项或若干项同时出现，都不能单独证明是项目绑定型软件。查询型、操作型、方法型Skill，以及只服务于Skill的本地辅助工具，不适用本门禁；继续由Skill Doctor按12维审核。

## 第一性原则

Skill是触发和运行环境入口，不是项目唯一大脑。项目业务、架构、API、数据、运维和验收合同必须跟随源码在canonical仓库版本化，使不加载该Skill的独立AI仍能接手项目。

## 权威分层

| 内容 | 正确归属 |
|---|---|
| 触发词、跨Skill路由、Hermes权限和交付约定 | Skill |
| 产品目标、业务规则、术语和验收场景 | GitHub仓库文档+测试 |
| 架构、API、数据模型、集成边界和ADR | GitHub仓库 |
| 部署、回滚、故障处理和项目命令 | 仓库文档+canonical脚本 |
| 可重复机械检查 | 仓库脚本/CI |
| 密钥、Token、生产Cookie | 受控secret存储，不进Skill或仓库 |
| 服务器实时连接事实 | 对应运维Skill或现场发现 |
| 单次任务进度、commit号、当前计数 | Git历史/审计产物，不写永久规则 |

## 审计流程

1. **识别项目绑定**：逐项证明“独立源码资产 + 独立维护生命周期 + 独立发布/部署边界”；任一项缺失即记录`not_applicable`。Skill Doctor只能提出转交候选，不能自行建仓、补项目合同或启动无Skill接管验收。
2. **冻结双方状态**：记录Skill包清单/hash、仓库worktree/branch/status/HEAD、项目文档和测试清单。
3. **建立知识归属矩阵**：逐节分类为Skill保留、仓库迁入、脚本化、历史归档或secret排除；禁止直接删长文。
4. **先建设仓库合同**：至少建立根 `AGENTS.md`、机器可读项目清单、文档索引、产品/架构/运维文档和无副作用doctor；稳定规则应有测试或机械门禁。
5. **无Skill接管验收**：独立审阅者只读取仓库，必须能定位目标、边界、命令、风险、发布和完成证据；失败则禁止瘦身Skill。
6. **再打薄Skill**：只保留触发、仓库发现、必读顺序、跨Skill路由、授权边界、输出和仓库drift阻断。
7. **验证双方**：运行仓库doctor/测试/build、Skill Doctor结构与语义复审、canonical所有权和目标Profile运行时可见性。
8. **发布分离**：本地commit、GitHub push和生产部署是三个不同门禁；用户只授权重构不自动包含push或部署。

## 最低仓库合同

推荐结构：

```text
AGENTS.md
PROJECT.yaml                 # 或等价机器可读manifest
README.md
docs/index.md
docs/product/
docs/architecture/
docs/operations/
docs/decisions/
scripts/project_doctor.py    # 无网络、无生产写入、失败非零退出
scripts/verify-project.sh    # 测试/build/静态门禁单一入口
.github/workflows/verify.yml # 适用时
```

文件名可按项目生态调整，但职责不能缺失。已有等价文件时复用，不为符合模板制造重复文档。

## 无Skill接管验收问题

只给独立AI仓库，必须能回答并引用仓库证据：

- 项目解决什么业务问题，关键术语是什么？
- 哪些数据和系统是权威源？
- 开工前运行什么命令，如何发现旧worktree或未提交改动？
- 普通功能、数据库、UI和跨系统变更分别如何验证？
- 如何部署、回滚和判断生产成功？
- 哪些动作必须取得用户确认？
- 文档、代码、测试或生产冲突时怎么办？

答案依赖外部Skill才能成立即FAIL。

## 机械验证

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/audit_project_bound_skill.py \
  --skill-dir /absolute/path/to/skill \
  --repo-dir /absolute/path/to/repository \
  --format json
```

机械脚本只验证最低结构、入口指针和明显重复风险；业务知识是否完整、归属是否正确、无Skill接管是否真实通过仍需语义审计。

## 完成门禁

- [ ] 知识迁移矩阵逐节守恒，缩减>30%有迁移目标和回滚副本
- [ ] 仓库doctor、测试、build和CI定义通过
- [ ] Skill明确先读仓库合同并在缺失时fail closed
- [ ] Skill不复制公式、API全表、数据库细节和长部署手册
- [ ] 独立无Skill接管验收通过
- [ ] Skill和仓库分别有Git/文件回滚点
- [ ] 未获授权时没有push、部署或生产写入

## 常见错误

1. **先删Skill再补仓库**：会造成不可逆知识损失；顺序必须仓库先、Skill后。
2. **把57份Reference原样搬进docs**：只是换目录，没有去重、脚本化或权威分层。
3. **README冒充项目合同**：README适合概览，不足以承载Agent权限、数据库和发布门禁。
4. **仓库文档复制代码细节**：字段/API可从代码生成时应生成或索引，不手写第二份易漂移清单。
5. **Skill Doctor顺手改业务代码**：Skill Doctor负责诊断、迁移合同和Skill质量；仓库改造由项目开发Skill执行。
6. **把本地commit当GitHub完成**：push是外部写入，必须单独授权并读回远端SHA。
