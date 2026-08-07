# 可执行生产示例审计门禁

用于审核部署、服务器、Nginx、systemd、Docker、数据库等Skill中的Shell命令块。目标不是证明生产环境成功，而是证明文档示例**不会因语法、授权时序或来源验证缺口误导Agent**。

## 1. Shell可执行性

- 提取所有`bash`/`sh`围栏，逐块运行`bash -n`；0个语法错误才通过。
- 可执行围栏里禁止使用`<app>`、`<domain>`、`<port>`等尖括号占位符：Shell会把它们解释为重定向。改用环境变量和缺值即停：

```bash
set -euo pipefail
: "${APP_DIR:?set verified app directory}"
: "${TARGET_SHA:?set exact target commit}"
```

- 只读展示模板或Markdown输出可保留尖括号，但必须位于`text`/`markdown`围栏，不得伪装成可直接运行的Shell。

## 2. Fail-fast与检查有效性

- 出现`test`、备份、安装、构建、重启等顺序动作时，检查失败必须阻止后续命令；推荐`set -euo pipefail`。
- `curl`验证使用`-f`并定义预期状态/内容；仅`-s`拿到HTTP 500仍可能退出0。
- “服务active/容器Up”不是业务成功，继续验证Commit/镜像、端口、health、真实业务入口和新日志。

## 3. 授权时序

- 文案应写“Simon下一条消息**严格等于**数字`1`”，不能写“包含数字1”或宽泛“已确认”。
- 备份创建、临时文件安装、证书dry-run/签发、`git fetch/reset`、依赖安装、容器构建/重建、API/数据库写入都属于状态变化；授权前只计算路径、生成diff和展示回滚，实际写入放到数字门禁之后。
- 一个授权只覆盖清单中精确列出的动作；新增范围需重新展示清单。

## 4. Git权威来源

`git cat-file -e <sha>`只证明本地对象存在，不证明来自当前GitHub权威分支。生产部署示例至少应：

```bash
set -euo pipefail
: "${DEFAULT_BRANCH:?set verified default branch}"
git fetch --prune origin "$DEFAULT_BRANCH"
git cat-file -e "${TARGET_SHA}^{commit}"
git merge-base --is-ancestor "$TARGET_SHA" "origin/$DEFAULT_BRANCH"
test -z "$(git status --porcelain)"
git reset --hard "$TARGET_SHA"
```

若项目要求目标必须等于远端HEAD而非历史祖先，再额外比较`TARGET_SHA`与`origin/$DEFAULT_BRANCH`；不要把该限制机械用于合法回滚。

## 5. 静态事实与外部阻塞

- IP、OS、端口、服务名、路径和应用清单若未实时验证，应标“历史快照/导航线索”，执行前从SSH alias、运行态和权威配置发现。
- 缺SSH alias/凭据等外部前提时，正确Skill应停止且禁止裸IP/猜密钥。此时可判`skill_quality=PASS`，但必须另记`production_runtime_verified=false`与阻塞原因，不能把包级审核写成生产验证。

## 验收证据

结果文件至少记录：命令块数量、`bash -n`结果、危险模式扫描、唯一canonical、四Profile可见性（如适用）、生产运行是否实际验证及阻塞原因。
