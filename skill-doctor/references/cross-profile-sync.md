# 跨 Profile Skill 共享与分叉

## 第一原则

先判断目标是：

1. **单一共享源**：多个 Profile 应执行完全相同的流程。
2. **独立分叉**：某个 Profile 有真实业务差异，需要独立维护。

不要把“复制到了多个目录”误认为“共享”。复制只是多个独立副本，会产生漂移。

## 推荐：单一共享源

Hermes Profile 不会自动继承 default 的本地 Skill。需要在子 Profile 的 `config.yaml` 使用官方配置：

```yaml
skills:
  external_dirs:
    - /absolute/path/to/canonical-skill-package
```

`external_dirs` 可以直接指向一个 Skill 包目录；若该包内还有嵌套 Skill，也会一起发现。例如：

```yaml
skills:
  external_dirs:
    - /Users/simon/.hermes/skills/xcode-build
    - /Users/simon/.hermes/skills/software-development/ios-development
```

这会共享 `xcode-build`、其嵌套的 `upload-to-testflight`，以及 `ios-development`，不会暴露 default 的整个 Skill 库。

## 全库拓扑审计方法

审计“哪些 Skill 应共享、哪些只是复制”时，必须同时看**物理实体**和**运行时可见性**：

1. 递归扫描 default 与所有 `~/.hermes/profiles/<name>/skills/**/SKILL.md`，不能只查顶层或 default。
2. 按 frontmatter `name` 分组，同时检测：
   - 跨 Profile 同名组；
   - 同一 Profile 内同名冲突；
   - 软链接；
   - 每个 Profile 的 `skills.external_dirs`。
3. 计算两种哈希：
   - `SKILL.md` 正文哈希；
   - 整个 Skill 包哈希（含 references/templates/scripts/assets）。
4. 计算包哈希时，遇到嵌套目录自己的 `SKILL.md` 就把它当独立 Skill 根，不把嵌套 Skill 混进父 Skill 哈希。
5. 用宽终端采集运行时清单，防止 Rich 表格把 Skill 名截成省略号：

```bash
COLUMNS=260 TERM=dumb NO_COLOR=1 hermes -p <profile> skills list
```

6. 区分来源后再下结论：
   - 自建 Skill 的相同包哈希：明确的物理复制；
   - 自建同名但多种包哈希：已经漂移，必须先 diff/合并；
   - builtin/official seed：由 Hermes 管理，不应机械迁到 `external_dirs`；
   - 官方本地改版：先用 `hermes skills list-modified` 与 `hermes skills diff` 确认。
7. 检查 `.archived` 目录和 `*.archived` 后缀。这些旧本地副本会污染审计：它们可能和官方同名 Skill 并存，也可能被错误地当成现行 canonical。处理顺序：先确认官方版本（`~/.hermes/hermes-agent/skills/` 或 `optional-skills/`），再删除归档目录，最后验证运行时可见性。
8. 报告中的数量和名单必须从同一原始数据集合生成；交付前做集合相等验证，不能手抄名单后只核对标题数字。

**常见误判：**

- CLI 显示 `local` 不证明存在本地物理副本，external source 也可能显示为 local。
- “只在某个 Profile 的物理目录不存在”不等于运行时不可见，插件、builtin、official 和 external source 都可能提供同名 Skill。
- “项目专属”不等于“Profile 专属”；多个 Profile 操作同一项目时，项目流程仍可只有一个 canonical。
- 通用 Skill 不等于必须给所有 Profile 注入；按真实使用范围共享，避免触发竞争和目录膨胀。

### 修改步骤

1. 递归扫描所有 Profile，确认同名 Skill 和支持文件分布。
2. 选择一个 canonical 包，合并各副本的独有 `references/`、`templates/`、`scripts/`。
3. 备份涉及的 Skill 包和各 Profile `config.yaml`。
4. 在子 Profile 配置 `skills.external_dirs` 指向 canonical 包。
5. 先运行 `hermes -p <profile> config check`。
6. 再运行 `hermes -p <profile> skills list`，确认目标 Skill 全部可见。
7. 最后删除旧副本，并再次运行第 5、6 步。

**顺序不能反：**先验证 external source 可见，再删副本。只做文件系统检查不算完成。

## 独立分叉时才复制

仅当 Profile 的工作流确实不同，才保留独立副本。复制整个 Skill 包，不能只复制 `SKILL.md`：

```text
SKILL.md
references/
templates/
scripts/
assets/
```

分叉版应在 frontmatter 或正文标明：

- canonical 来源
- 分叉原因
- 哪些章节允许不同
- 后续同步策略

## 禁止方案

- 不用 symlink 连接 Profile Skill。
- 不把 default 整个 `skills/` 暴露给专用 Profile，除非明确需要全部能力。
- 不在删除副本后才第一次验证 Skill 可见性。
- 不看到 `hermes skills list` 的 `local` 标签就推断存在物理副本；以实际路径扫描和 `external_dirs` 配置共同判断。

## 迁移与验证 Pitfalls

### 1. 运行时不可见不一定是迁移失败

删除副本前先读 frontmatter。带有 `environments` 或 `platforms` 限制的 Skill 可能故意不出现在普通 Profile 的 `skills list`。例如：

```yaml
environments: [kanban]
```

对此类 Skill：验证 canonical 包、`external_dirs`、frontmatter 和原有环境限制；在对应环境或显式 force-load 路径验证。不要为了让普通清单出现而删除环境限制。

### 2. 只把 frontmatter 当 YAML

`SKILL.md` 只有首尾 `---` 之间是 YAML。唯一性和名称检查必须先提取 frontmatter；直接对整份 Markdown 执行 `yaml.safe_load` 会把有效 Skill 误判成 0 命中。

### 3. 哈希必须同口径

审计与迁移脚本若对嵌套 Skill、隐藏文件或缓存文件的处理不同，会出现移动后哈希变化的假告警。遇到不一致时先停止当前批次，然后：

1. 用备份和目标做递归文件级 diff；
2. 用同一函数生成移动前后“相对路径 + 每文件 SHA-256”清单；
3. 清单完全一致才继续。

不要仅凭旧摘要哈希不同断言文件损坏。

### 4. 备份排除规则用相对路径

备份根本身通常位于 `~/.hermes/backups/...`。若计数脚本检查绝对路径是否含 `backups`，会把整个快照误排除为 0。应先相对到每个快照 Skill 根，再过滤其内部 `.archive`、`backups`、`state-snapshots`。

### 5. 展示管道不要污染真实退出码

`hexdump | sed -n ...` 等展示管道在 `pipefail` 下可能因下游提前关闭触发 SIGPIPE，使配置检查已成功但总命令返回 1。完成证据应独立采集：

- YAML 结构化读回指定字段；
- 每个 `hermes -p <profile> config check` 的独立退出码；
- 展示/截断命令不和真实验证放在同一个 pipefail 管道。

### 6. 同名冲突先合并支持文件

同一 Profile 内两个同名 Skill 不能只比较 `SKILL.md`。安全流程：

1. 选职责正确的主文作骨架；
2. 汇总所有副本的 `references/templates/scripts/assets`；
3. 独有文件直接收拢；
4. 同名不同内容文件逐个语义合并或改成明确的新文件名；
5. 更新 References 索引；
6. 验证显式引用和运行时可见性后再删旧包。

不要按 mtime、行数或“看起来更丰富”直接覆盖。

## 完成证据

必须同时具备：

```text
backup_validation=PASS
canonical_path=<唯一源路径>
physical_override_count=0
hermes -p default skills list=<visible-or-documented-environment-filter>
hermes -p work skills list=<visible-or-documented-environment-filter>
hermes -p work-web skills list=<visible-or-documented-environment-filter>
hermes -p finance skills list=<visible-or-documented-environment-filter>
config_check=PASS for every modified profile
frontmatter_parse=PASS
explicit_reference_paths=PASS
```

大批量迁移还应保存机器可读 manifest：canonical、原路径、动作、逐文件哈希、已删除路径和例外原因。会话或工具调用中断后从 manifest 继续，不重新猜进度。

## 归档清理 checklist

迁移前若发现 `.archived` 目录或同名归档 Skill：

- [ ] 确认官方/现行版本存在且运行时可见；
- [ ] 不要以 `.archived` 作为 canonical 源；
- [ ] 删除 `.archived` 目录后，运行 `hermes -p <profile> skills list` 确认目标 Skill 仍然可见；
- [ ] 如果归档版是唯一的本地源，先迁移到 canonical 路径或合并到现有 canonical，再删除。

## 官方边界示例

- `axolotl`、`unsloth`：default 的 `*.archived` 是 stub，work/work-web 来自 `~/.hermes/hermes-agent/optional-skills/...`。不要自建 canonical；如需统一，走官方 `hermes skills reset/update`。
- `nano-pdf`、`ocr-and-documents`：存在官方 builtin、`.archived` 本地副本和本地修改版混合。先 `hermes skills diff` 确认官方状态，再清理归档副本，再决定是否共享本地修改。

已有长会话的系统提示词不会中途重建；新 Skill 目录应在新会话中生效，不需要因此自主重启 Gateway。
