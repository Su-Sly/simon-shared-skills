# 批量治理规则铺设

用于给一类现有 Skill 批量加入统一门禁、交付规则、验证规范或安全约束。目标是完整覆盖 canonical 活跃 Skill，同时避免污染官方包、归档、通用方法论和纯数据操作 Skill。

## 范围发现：双向盘点

### 1. 正向扫描

递归扫描所有 Profile 的活跃 `SKILL.md`，不能只看 default，也不能只按目录名判断：

```bash
find ~/.hermes -path '*/skills/*/SKILL.md' -print
```

先排除：

- `~/.hermes/hermes-agent/` 内置与 optional Skill
- `.archive`、`.archived`、backup、restore 临时副本
- 同名 Skill 的非 canonical 历史副本

读取 frontmatter 的 `name`、`description`、`triggers` 和正文职责。关键词必须覆盖中英文，例如 `维护|部署|应用|网站|maintain|deploy|web app|application`；单一语言会漏掉旧 Skill。

### 2. 职责分类

| 类别 | 是否铺设应用交付门禁 | 判断依据 |
|---|:---:|---|
| 具体网站/应用维护 Skill | 是 | 对应明确域名、产品或运行实例 |
| 应用部署/维护 umbrella | 是 | 明确治理一组应用的交付流程 |
| 通用设计模式/方法论 | 否 | 不对应具体应用状态，内容不应随某个应用变化 |
| 纯数据操作 Skill | 否 | 只做查询、录入、查重、同步，不维护应用本身 |
| 官方/Hub/归档 Skill | 否 | 非自建 canonical，升级或归档边界不同 |

### 3. 反向漏项扫描

初始候选清单形成后，再从全部活跃自建 Skill 中反向找：

- 域名、端口、部署目录、systemd/Docker/nginx
- “维护、更新、部署、App、WebUI、service”等职责描述
- 旧 Profile 下的窄目录名或英文 description

将所有未入选命中项逐一分类并写明排除理由。**反向扫描完成前，不得宣布范围已锁定。**

## 修改流程

1. 确认 canonical 路径与 Profile 拓扑。
2. 对最终目标集做统一备份，保留相对目录结构。
3. 用同一段标准文本做精准 patch；每个文件只允许出现一次治理门禁。
4. 全量回读，检查 YAML、代码围栏、引用、统一文本哈希和意外 diff。
5. 用 `skill-doctor` 批量模式审核：新规则引入的 ⚠️/❌ 必须清零；既有非阻塞结构债单独记录，不能借题大改。
6. 逐 Profile 执行 `config check` 和 `skills list --enabled-only`，文件存在不等于运行时可见。
7. 最终修改后从零重跑验证，不能沿用补漏前的通过结论。

## 常见坑

- **先报数量再反向扫描**：容易漏掉英文 description、旧 Profile 和命名不直观的 Skill。
- **只靠目录或关键词自动修改**：会把治理规则塞进数据操作、通用方法或官方副本。
- **补漏后只验证新增文件**：初始候选集全部通过，不能证明扩充后的最终目标集仍然通过；必须从零全量重跑。
- **把“保持最新”写成流水账**：治理门禁应维护当前有效状态，禁止写 commit、临时任务进度和会话日志。
- **审核顺手重构全部旧债**：只修本次引入问题和阻塞可靠执行的既有 ❌；大规模瘦身另开任务。
