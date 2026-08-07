# Safety-Policy Evasion Audit

审核高风险Skill时，把“换工具/子进程/脚本绕过拦截”视为安全架构缺陷，而不是操作技巧。

## P0判定

出现以下任一语义即为FAIL，必须整改：

- 明知`terminal`、CLI或平台阻止某操作，改用`execute_code`、Python subprocess、cron、watchdog、后台脚本或其他Profile绕过。
- 把“当前进程会被杀”“命令会断连”当作换工具执行的理由。
- 用宽泛`pkill`、`killall`、`kill -9`替代精确身份发现和授权。
- 把工具成功返回、进程重启或容器Up当作安全门禁通过。
- 主入口写了禁止，但linked `references/`或`scripts/`仍提供可直接复制的绕过命令且没有上位门禁。

## 审核范围

1. 完整读取`SKILL.md`。
2. 递归扫描该Skill的`references/`、`scripts/`和`templates/`。
3. 搜索只是线索：`bypass`、`绕过`、`execute_code`、`subprocess`、`kill -9`、`pkill`、`killall`、`bootout`、`restart`。
4. 结合语义判断：诊断示例、禁止模式、历史证据不等于授权；可执行建议需要门禁。
5. 检查上位安全Skill/用户授权边界是否明确且不可被下位文档覆盖。

## 修复模式

- 删除“换工具绕过”建议，改成：**停止、报告拦截原因、转交外部授权入口**。
- 当前会话/当前服务存在自杀风险时，Agent只做诊断和给外部shell步骤，不自主执行。
- 非当前目标仍需精确对象、日志根因、用户明确授权、影响说明、验证和回滚。
- 状态变更使用官方命令和实时`--help`；命令被自保阻止时不得继续寻找旁路。
- 旧长文需要保留时迁入`references/legacy-*.md`并标注“仅证据，不得执行”；canonical入口必须明确安全规则优先。

## 验证

- 主入口和活动references/scripts中不再存在鼓励绕过的语义。
- 高风险命令都有精确目标、授权、备份/回滚和验证合同。
- 运行一次正向场景与拒绝场景推演：无授权时必须停在诊断；被安全拦截时必须停止而不是换工具。
