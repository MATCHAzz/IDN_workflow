# 本次周报执行流程与文件访问关系

运行：`weekly-20261017-057d104f`。本期 2026-10-11 至 2026-10-17，比较期 2026-10-04 至 2026-10-10，时区 Asia/Jakarta。

说明：工具调用顺序来自本次 e*.json 证据；程序内部模块链根据当前代码还原。项目没有记录系统级的逐文件打开日志，因此下面区分 Agent 主动阅读、程序执行和保存产物。

## 一、Agent 主动读取任务指引与知识

本次读取了：

- [skills/weekly-report-update/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/weekly-report-update/SKILL.md>)：确定完整周报流程和异常处理分支。
- [skills/business-kpi-analysis/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/business-kpi-analysis/SKILL.md>)：确定知识读取、逻辑数据源、SQL 提交与指标核对要求。
- [skills/business-report-writing/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/business-report-writing/SKILL.md>)：确定证据汇总、报告导出和待推送流程。
- [knowledge/README.md](</Users/matchalee/Desktop/IDN Workflow/knowledge/README.md>)：理解知识库结构。
- [knowledge/metrics.json](</Users/matchalee/Desktop/IDN Workflow/knowledge/metrics.json>)：读取五指标口径、单位与去重要求。
- [knowledge/schema.json](</Users/matchalee/Desktop/IDN Workflow/knowledge/schema.json>)：读取可查询逻辑数据源、字段、粒度和关联规则。
- [knowledge/rules.md](</Users/matchalee/Desktop/IDN Workflow/knowledge/rules.md>)：读取周报、告警与结果字段约定。
- [config/operations_metrics.json](</Users/matchalee/Desktop/IDN Workflow/config/operations_metrics.json>)：读取统一有效直播、告警和样本门槛。
- [knowledge/sql_examples/period_metrics.sql](</Users/matchalee/Desktop/IDN Workflow/knowledge/sql_examples/period_metrics.sql>)：主动审阅并采用标准整体五指标查询。
- [knowledge/sql_examples/period_comparison.sql](</Users/matchalee/Desktop/IDN Workflow/knowledge/sql_examples/period_comparison.sql>)：主动审阅并采用标准整体及层级比较查询。

同时运行 `.venv/bin/python -m liveops tools` 查看工具目录。该命令经过 `liveops/__main__.py` 和 `liveops/tools.py`，没有执行业务查询。

## 二、建立本次运行与输入文件

新建独立的请求目录 [outputs/requests/weekly-20261017-057d104f](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f>)，写入以下输入：

- [profile.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/profile.json>)：空参数，供快照检查。
- [knowledge.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/knowledge.json>)：topic=weekly_report。
- [prepare.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/prepare.json>)：workflow=weekly_report，report_date=2026-10-17。

## 三、每次工具调用共用的入口

`参数 JSON → liveops/__main__.py → ToolRegistry.call（liveops/tools.py）→ 目标工具 → 保存 e*.json`。

- [__main__.py](</Users/matchalee/Desktop/IDN Workflow/liveops/__main__.py>) 解析 `call`、`--run-id` 和 `--args-file`，读取参数 JSON。
- [tools.py](</Users/matchalee/Desktop/IDN Workflow/liveops/tools.py>) 校验调用、预留证据编号、打开只读连接、检查快照和知识版本。
- [store.py](</Users/matchalee/Desktop/IDN Workflow/liveops/store.py>) 连接 [liveops.sqlite](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/liveops.sqlite>)，读取元数据并记录 SQL 查询。
- [knowledge.py](</Users/matchalee/Desktop/IDN Workflow/liveops/knowledge.py>) 读取指标、结构和配置，计算 knowledge_id/config_id。

版本计算会读取 knowledge 目录内的 Markdown、JSON 和 SQL 文件的字节，包括 boost_candidates.sql 与 sql_examples/README.md；这是版本校验，不代表这次执行了助推查询。

## 四、实际工具调用顺序

| 顺序 | 输入文件 | 工具与处理 | 证据 |
| --- | --- | --- | --- |
| e0001 | [profile.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/profile.json>) | get_data_profile：确认快照覆盖、时区及可用活动。 | [e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0001.json>) |
| e0002 | [knowledge.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/knowledge.json>) | read_business_knowledge：返回周报知识、配置和版本。 | [e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0002.json>) |
| e0003 | [prepare.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/prepare.json>) | prepare_analysis：确定两周窗口与全主播范围，执行质量门禁。 | [e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0003.json>) |
| e0004 | [current_metrics.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/current_metrics.json>) | execute_readonly_sql：执行本周整体五项指标。 | [e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0004.json>) |
| e0005 | [weekly_comparison.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/weekly_comparison.json>) | execute_readonly_sql：比较整体、头部、腰部、尾部的五项指标并计算告警。 | [e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0005.json>) |
| e0006 | [tail_streamer_comparison.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_streamer_comparison.json>) | execute_readonly_sql：告警后下钻尾部主播，两周同名单比较。 | [e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0006.json>) |
| e0007 | [tail_diagnostic_summary.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_diagnostic_summary.json>) | execute_readonly_sql：初版汇总含通配符，被 STAR_DENIED 拒绝。此输入文件随后修正；初版原文保存在本证据的 arguments.sql。 | [e0007.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0007.json>) |
| e0008 | [tail_diagnostic_summary.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_diagnostic_summary.json>) | execute_readonly_sql：改为显式列名后成功，统计下降覆盖、供给变化与损失集中度。 | [e0008.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0008.json>) |
| e0009 | [assemble.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/assemble.json>) | assemble_analysis：仅汇总本次成功查询证据。 | [e0009.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0009.json>) |
| e0010 | [export.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/export.json>) | export_report：渲染报告并复制其引用的证据。 | [e0010.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0010.json>) |
| e0011 | [delivery.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/delivery.json>) | prepare_delivery：生成待推送草稿、完成状态和工作台导航。 | [e0011.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0011.json>) |

## 五、准备范围与质量门禁的内部路径

`prepare.json → __main__.py → tools.py → sql_tools.py.prepare_analysis → sql_analysis.py.prepare → validation.py → store.py → liveops.sqlite → e0003.json`。

- [sql_analysis.py](</Users/matchalee/Desktop/IDN Workflow/liveops/sql_analysis.py>) 确定本期、前期与主播范围，只准备范围，不编写业务 SQL。
- [validation.py](</Users/matchalee/Desktop/IDN Workflow/liveops/validation.py>) 检查日期、关联、覆盖、支付对账、开播和助推日志完整性。

后续 SQL、汇总、导出和待推送步骤也会在相应入口重新检查质量或版本，不是只检查一次。

## 六、SQL 是怎样进入执行工具的

前两条查询采用 Agent 已审阅的知识库标准 SQL 结构；尾部两条查询是根据这次告警编写的补充分析。

| 来源/目的 | 提交 SQL 文件 | 实际传给 CLI 的参数文件 | 成功证据 |
| --- | --- | --- | --- |
| period_metrics.sql → 本周整体指标 | [current_metrics.sql](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/current_metrics.sql>) | [current_metrics.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/current_metrics.json>) | [e0004](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0004.json>) |
| period_comparison.sql → 整体与层级比较 | [weekly_comparison.sql](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/weekly_comparison.sql>) | [weekly_comparison.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/weekly_comparison.json>) | [e0005](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0005.json>) |
| 告警后编写 → 尾部主播比较 | [tail_streamer_comparison.sql](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_streamer_comparison.sql>) | [tail_streamer_comparison.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_streamer_comparison.json>) | [e0006](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0006.json>) |
| 下钻后编写 → 尾部下降汇总 | [tail_diagnostic_summary.sql](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_diagnostic_summary.sql>) | [tail_diagnostic_summary.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_diagnostic_summary.json>) | [e0008](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0008.json>) |

Agent 先把 `.sql` 文本读入对应 JSON 的 `sql` 字段，再通过 `--args-file` 提交。执行工具读取的是 JSON 中的 SQL 字符串，不会按文件名自行选择查询。

每条 SQL 的执行路径：

`参数 JSON → __main__.py → tools.py → sql_tools.py.execute_readonly_sql → sql_analysis.evidence 读取 e0003 → knowledge.contract 校验知识 → validation.require_quality → sql_guard.py → store.py → liveops.sqlite → sql_analysis.validate_rows → e*.json`。

- [sql_tools.py](</Users/matchalee/Desktop/IDN Workflow/liveops/sql_tools.py>) 绑定日期、口径与样本门槛，限制追加筛选不能扩大范围。
- [sql_guard.py](</Users/matchalee/Desktop/IDN Workflow/liveops/sql_guard.py>) 检查 SELECT/WITH、逻辑数据源、聚合与用户字段限制，注入限定范围的逻辑数据源。
- [store.py](</Users/matchalee/Desktop/IDN Workflow/liveops/store.py>) 以只读方式执行并限制时限与返回行数。

普通 Agent SQL 使用 watch_events、gift_events、broadcast_days、streamer_profiles；工具映射到数据库中的观看、成功打赏、开播日志与主播维度。CSV 没有作为本次查询输入。

## 七、发现告警后才读取的文件

在 e0005 返回尾部观看告警后，Agent 主动读取：

- [SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/anomaly-monitoring/SKILL.md>)：核对日期、名单、基线、样本和规则。
- [SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/root-cause-drilldown/SKILL.md>)：确定相关主播下钻，证据足够后停止。

随后执行 e0006，再执行汇总查询。e0007 因 SQL 通配符限制失败，修正为显式列名后产生 e0008；失败证据保留，未用于报告。

## 八、汇总前的语义核对

Agent 读取本次 e0003、e0004、e0005、e0006、e0008，检查任务范围、版本、整体指标一致性与尾部可加指标勾稽，并保存 [semantic_review.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/semantic_review.json>)。业务数值、差值与统计均来自 SQL；核对脚本只比较已有结果。

随后写入 [assemble.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/assemble.json>)，提交 e0004、e0005、e0006、e0008，引用同一范围证据 e0003。

`assemble.json → sql_tools.py.assemble_analysis → sql_analysis.py.assemble → validation.py → e0009.json`。

## 九、报告导出

Agent 写定性观察、候选解释与下一步，全部引用已汇总的 e0009，保存 [export.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/export.json>)。

`export.json → sql_tools.py.export_report → report.py.export → report.py.render → 报告文件 → e0010.json`。

生成：

- [report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/report-95aa31d60b6e/report.md>)。
- [report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/report-95aa31d60b6e/report.html>)。
- [report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/report-95aa31d60b6e/report.json>)。

报告目录同时复制 e0003、e0004、e0005、e0006、e0008、e0009，供报告链接追溯；e0007 不在报告证据中。

## 十、SQL 展示文档

在汇总之后、报告导出之前，Agent 从成功证据提取 submitted_sql、prepared_sql 和 bound_parameters，保存 [SQL_USED.md](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/SQL_USED.md>)。以下 `.prepared.sql` 是事后从执行证据提取并格式化的副本，不是另一轮查询输入：

- [current_metrics.prepared.sql](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/current_metrics.prepared.sql>)。
- [weekly_comparison.prepared.sql](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/weekly_comparison.prepared.sql>)。
- [tail_streamer_comparison.prepared.sql](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_streamer_comparison.prepared.sql>)。
- [tail_diagnostic_summary.prepared.sql](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_diagnostic_summary.prepared.sql>)。

## 十一、待推送包与工作台

输入 [delivery.json](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/delivery.json>)，引用分析 e0009 和报告 e0010。

`delivery.json → sql_tools.py.prepare_delivery → 校验分析/报告 → delivery_draft.json → workflow_state.json → workspace.py.workspace_index → outputs/operations/index.html → e0011.json`。

生成或更新：

- [delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/delivery_draft.json>)：draft_not_sent，未配置发送目标与定时时间。
- [workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/workflow_state.json>)：completed 表示本地报告和待推送包完成，不表示已发送或已人工审批。
- [index.html](</Users/matchalee/Desktop/IDN Workflow/outputs/operations/index.html>)：更新为本次周报看板入口；其余任务导航按各自完成记录选择。

## 十二、最终查看与检查

确认产物存在、HTML 中的本地报告/证据链接有效、工作台指向本次运行、草稿状态未发送。随后通过仅本机可访问的预览服务打开 report.html，查看页面和核心指标显示，并打开 SQL_USED.md。没有修改源数据库或下发流量。

## 本次没有走的执行路径

本次通过聊天中的 Agent 逐步调用工具完成，未调用 run-plan，因此未运行 liveops/plan_runner.py，也未使用 examples/sql_plans/weekly_report.json。docs/SQL_PLAN_FORMAT.md 无需参与此次执行。

没有执行 init 或 ops_mock.generate，没有调用固定查询 query_gift_total/simple_query，也没有运行测试。__main__.py 导入初始化模块不等于调用了数据生成函数。业务查询没有读取旧数据快照、历史报告或生成器事件答案。
