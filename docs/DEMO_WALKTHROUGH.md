# 旧版支付诊断演示（历史存档）

当前主线已改为周报、活动复盘和主播助推。请使用[运营自动化流程说明](OPERATIONS_WORKFLOW.md)；下文保留旧快照上的执行记录，不作为当前默认示例。旧工具实现及命令已删除，仅可查看历史产物。

本样例由当前 Codex 单 Agent 在开发完成后读取业务 Skills，并实际调用 Python 工具生成。没有运行一个写死问句的“Agent 脚本”。这是一轮功能演示，不是盲测；开发过程已接触方案中的事件设计，不将本样例当作独立 Agent 准确率评测。

## 主问题

> 分析 2026-10-15 印尼直播为什么支付表现下降，给出证据和下一步建议，并保存报告。

本任务 `run_id=demo-payment-20261015`，所有日期为 Asia/Jakarta。按顺序执行：

| 证据 | 实际调用 | 目的与后续决策 |
| --- | --- | --- |
| [e0001](../outputs/runs/demo-payment-20261015/e0001.json) | get_data_profile | 确认数据覆盖目标日及此前七日 |
| [e0002](../outputs/runs/demo-payment-20261015/e0002.json) | get_metric_dictionary | 区分付费转化率、支付成功率和 GMV |
| [e0003](../outputs/runs/demo-payment-20261015/e0003.json) | check_data_quality | 目标日及基线范围质量检查通过 |
| [e0004](../outputs/runs/demo-payment-20261015/e0004.json) | query_kpis | 先查看观看 → 付费 → 支付成功 → GMV 链路 |
| [e0005](../outputs/runs/demo-payment-20261015/e0005.json) | detect_anomalies | 判断支付成功率/付费转化下降是否超过规则阈值 |
| [e0006](../outputs/runs/demo-payment-20261015/e0006.json) | get_dimension_breakdown(platform) | 支付链路异常后选择平台下钻；看到 Android 与 iOS 差异后停止扩维 |
| [e0007](../outputs/runs/demo-payment-20261015/e0007.json) | export_report | 选取当前证据；添加引用证据的定性观察、假设和下一步；工具渲染数字 |

工具执行证据中的 `skill` 字段来自注册表映射，代表所属能力，**单靠它不能证明模型读取了 Skill**。本轮聊天工具记录另有 SKILL.md 的实际读取。未来演示也应保留 Agent 的读取/调用记录，避免只展示脚本输出。

## 得到的结论

质量门禁通过。观看 UV 为 1,750，较前七日中位数上升 29.06%；支付成功率为 47.22%，较 94.24% 的基线下降 47.01 个百分点。付费转化率由基线 11.54% 降至 7.66%，下降 3.88 个百分点。Gross GMV 为 8,900,000 IDR，较基线下降 27.82%，未达到当前三成的 GMV 告警阈值。

平台拆解发现 Android 支付成功率 33.33%，其自身历史中位数为 93.88%；iOS 为 92.16%，其历史中位数为 94.38%，未触发同样的下降阈值。Android 组内成功率的负向效应为 -46.96 pp；贡献基线另用前七日合并成功率，整体变化为 -47.60 pp，详见 e0006，不能与中位数告警的 -47.01 pp 混用。

因此先调查 Android 支付错误码、应用版本、支付方式和网关返回日志；当前聚合数据只能支持端别异常线索，无法证明具体故障，也没有足够证据给出 GMV 变化的因果归因。平台拆解已足以提出下一步，因此没有固定再跑渠道和主播层级。

以上数字直接来自 e0004、e0005、e0006。正式报告由工具自动排版：[Markdown](../outputs/runs/demo-payment-20261015/report-c5c634e8d765/report.md) / [HTML](../outputs/runs/demo-payment-20261015/report-c5c634e8d765/report.html)。

## 再试不同意图

- 事实型：“只查 2026-10-15 Android 支付成功率。” → KPI Skill + platform 筛选即可，不要求异常诊断和完整报告。
- 分层型：“2026-10-13 风险规则命中的流水占比多少？” → audience-segmentation；[本轮实算结果](../outputs/runs/demo-risk-20261013/e0001.json)为 48 位待复核付费用户，规则命中 GMV 144,000,000 IDR，占 91.61%，不是已证实欺诈。
- 缺数据：“帮我算 2026-10-15 退款率。” → 字典中没有退款数据；[实际调用](../outputs/runs/demo-unknown-metric/e0001.json)返回 `UNSUPPORTED_METRIC`，不编造百分比。
- 范围外：“分析昨天。” → 先说明本快照截至 2026-10-17，再按实际日期判断是否覆盖，不静默改成一个有数据的日期。

这些记录仅说明当时的执行情况。当前演示请使用运营流程Skills或examples/sql_plans/中的SQL计划；旧工具名称不再是可调用入口。
