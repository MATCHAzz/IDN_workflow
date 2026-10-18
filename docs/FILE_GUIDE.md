# 项目逐文件说明

整理日期：2026-10-18。以下说明来自当前目录、文档、代码职责和产物元数据；未重新运行分析或验证业务结果。

## SQL_PLAN_FORMAT.md 有什么用

它规定“已经写好的 SQL 分析计划”如何保存为 JSON，供 `run-plan` 按固定步骤重放。自然语言理解、SQL 编写以及新问题的下钻选择仍由当前聊天中的 Agent 完成。

计划中的 `workflow` 指定任务；`report_date` 或 `campaign_id` 确定范围；`queries` 按顺序记录 SQL 及结果类型；`sql_file` 相对计划文件目录解析；`sql` 可直接保存查询文本，两者选一。`only_if_alerts` 只在之前已有查询告警时执行该项；`notes` 保存定性备注。日期、口径和名单限制由执行工具绑定。

对应关系：`docs/SQL_PLAN_FORMAT.md` 说明格式 → `examples/sql_plans/*.json` 保存具体计划 → `knowledge/sql_examples/*.sql` 保存查询 → `liveops/plan_runner.py` 重放 → `outputs/runs/` 保存结果。

## 根目录、文档、配置、知识、Skills、SQL 示例与代码

| 文件 | 大致内容与用途 |
| --- | --- |
| [.gitignore](</Users/matchalee/Desktop/IDN Workflow/.gitignore>) | 规定 Git 忽略虚拟环境、缓存与部分运行产物，同时保留指定演示运行目录。 |
| [AGENTS.md](</Users/matchalee/Desktop/IDN Workflow/AGENTS.md>) | 给项目 Agent 的执行规则：任务路由、SQL 访问约束、证据管理和交付边界；Agent 接任务时遵守。 |
| [HANDOFF.md](</Users/matchalee/Desktop/IDN Workflow/HANDOFF.md>) | 项目交接说明：已完成内容、架构、未接入能力、已有产物和继续工作的顺序。 |
| [README.md](</Users/matchalee/Desktop/IDN Workflow/README.md>) | 项目使用入口：安装、自然语言任务示例、固定查询、计划重放和关键限制。 |
| [config/operations_metrics.json](</Users/matchalee/Desktop/IDN Workflow/config/operations_metrics.json>) | 可执行规则的统一配置：有效直播门槛、下降提醒阈值、样本门槛和助推资格与额度。 |
| [docs/ACCEPTANCE.md](</Users/matchalee/Desktop/IDN Workflow/docs/ACCEPTANCE.md>) | 说明现有自动验证覆盖的范围、复验命令以及尚未验证的边界。 |
| [docs/DEMO_WALKTHROUGH.md](</Users/matchalee/Desktop/IDN Workflow/docs/DEMO_WALKTHROUGH.md>) | 旧版支付诊断演示的历史执行记录；旧工具已删除，供回顾，不作为当前操作指南。 |
| [docs/FILE_GUIDE.md](</Users/matchalee/Desktop/IDN Workflow/docs/FILE_GUIDE.md>) | 本文件：逐个解释项目文件、历史数据及运行产物，并说明相互关系。 |
| [docs/OPERATIONS_WORKFLOW.md](</Users/matchalee/Desktop/IDN Workflow/docs/OPERATIONS_WORKFLOW.md>) | 当前业务链路的完整说明：数据源、五项指标、三类任务、工具调用和交付状态。 |
| [docs/SQL_PLAN_FORMAT.md](</Users/matchalee/Desktop/IDN Workflow/docs/SQL_PLAN_FORMAT.md>) | 已保存 SQL 计划的 JSON 格式说明：任务范围、查询顺序、SQL 引用、结果类型、条件执行和重放约束。 |
| [examples/sql_plans/campaign_review.json](</Users/matchalee/Desktop/IDN Workflow/examples/sql_plans/campaign_review.json>) | 保存的活动复盘计划：指定活动，执行同名单的本期指标和前后比较。 |
| [examples/sql_plans/tail_streamers.sql](</Users/matchalee/Desktop/IDN Workflow/examples/sql_plans/tail_streamers.sql>) | 尾部主播下钻 SQL 参考，按主播聚合期间观看 UV 和看播时长。 |
| [examples/sql_plans/traffic_boost_update.json](</Users/matchalee/Desktop/IDN Workflow/examples/sql_plans/traffic_boost_update.json>) | 保存的助推更新计划：执行近期整体指标和主播建议清单，再导出待审核产物。 |
| [examples/sql_plans/weekly_report.json](</Users/matchalee/Desktop/IDN Workflow/examples/sql_plans/weekly_report.json>) | 保存的周报计划：本期指标、周期比较，以及已有告警时才执行的尾部主播补充查询。 |
| [knowledge/README.md](</Users/matchalee/Desktop/IDN Workflow/knowledge/README.md>) | 知识库导航，说明各知识文件职责及 Agent 如何读取后编写 SQL。 |
| [knowledge/metrics.json](</Users/matchalee/Desktop/IDN Workflow/knowledge/metrics.json>) | 五项指标的定义、单位、聚合公式、零值和 UV 去重要求。 |
| [knowledge/rules.md](</Users/matchalee/Desktop/IDN Workflow/knowledge/rules.md>) | 周报、活动、助推及告警规则，并规定不同 SQL 结果必须返回的字段。 |
| [knowledge/schema.json](</Users/matchalee/Desktop/IDN Workflow/knowledge/schema.json>) | Agent 可查询的逻辑数据源、字段、数据粒度、关联方法及保留参数。 |
| [knowledge/sql_examples/README.md](</Users/matchalee/Desktop/IDN Workflow/knowledge/sql_examples/README.md>) | SQL 参考的使用方法：先读口径再修改和执行，并要求核对业务语义。 |
| [knowledge/sql_examples/boost_candidates.sql](</Users/matchalee/Desktop/IDN Workflow/knowledge/sql_examples/boost_candidates.sql>) | 计算主播级指标、助推资格、建议额度，以及相对昨日额度的增减建议。 |
| [knowledge/sql_examples/period_comparison.sql](</Users/matchalee/Desktop/IDN Workflow/knowledge/sql_examples/period_comparison.sql>) | 比较本期与基线的五项指标，含整体和主播层级、差值、变化率及告警状态。 |
| [knowledge/sql_examples/period_metrics.sql](</Users/matchalee/Desktop/IDN Workflow/knowledge/sql_examples/period_metrics.sql>) | 计算所选窗口与名单的整体五项指标；先分别聚合事实数据再关联。 |
| [liveops/__init__.py](</Users/matchalee/Desktop/IDN Workflow/liveops/__init__.py>) | Python 包初始化，定义指标版本、规则版本和业务时区常量。 |
| [liveops/__main__.py](</Users/matchalee/Desktop/IDN Workflow/liveops/__main__.py>) | 命令行入口；解析 init、tools、call、run-plan 以及数据、输出和参数文件选项。 |
| [liveops/knowledge.py](</Users/matchalee/Desktop/IDN Workflow/liveops/knowledge.py>) | 读取知识库和配置，检查配置有效性，计算 knowledge_id 与 config_id 以识别版本变化。 |
| [liveops/ops_mock.py](</Users/matchalee/Desktop/IDN Workflow/liveops/ops_mock.py>) | 生成当前运营 Demo 的合成 SQLite、CSV 和快照说明；普通业务分析不能用生成逻辑当业务证据。 |
| [liveops/plan_runner.py](</Users/matchalee/Desktop/IDN Workflow/liveops/plan_runner.py>) | 读取已保存 JSON 计划及 SQL，依次调用固定工具；处理条件查询、重复重放和失败记录，不调用模型。 |
| [liveops/report.py](</Users/matchalee/Desktop/IDN Workflow/liveops/report.py>) | 从保存的工具证据渲染 Markdown、JSON、HTML 报告，复制证据并导出助推 CSV。 |
| [liveops/simple_query.py](</Users/matchalee/Desktop/IDN Workflow/liveops/simple_query.py>) | 保留的一条固定业务查询：计算指定日期范围的成功打赏金额，用于学习与对照。 |
| [liveops/sql_analysis.py](</Users/matchalee/Desktop/IDN Workflow/liveops/sql_analysis.py>) | 确定任务日期与主播范围，校验查询结果字段及数值关系，将同任务 SQL 证据汇总成分析结果。 |
| [liveops/sql_guard.py](</Users/matchalee/Desktop/IDN Workflow/liveops/sql_guard.py>) | 检查 Agent SQL 的语法树、数据源、函数和聚合限制，注入限定日期与名单的逻辑数据源后只读执行。 |
| [liveops/sql_tools.py](</Users/matchalee/Desktop/IDN Workflow/liveops/sql_tools.py>) | 面向 Agent 的 SQL 工具接口；串联准备范围、执行、质量门禁、知识版本核对、汇总、导出和待推送。 |
| [liveops/store.py](</Users/matchalee/Desktop/IDN Workflow/liveops/store.py>) | 底层 SQLite 只读连接、权限检查、执行时限、结果行数限制和 SQL 查询日志。 |
| [liveops/tools.py](</Users/matchalee/Desktop/IDN Workflow/liveops/tools.py>) | 工具注册与调用总入口；校验工具名和参数，检查快照，分配证据编号并保存调用记录。 |
| [liveops/validation.py](</Users/matchalee/Desktop/IDN Workflow/liveops/validation.py>) | 公共质量、日期和范围校验；检查重复、关联、日期覆盖、支付对账、开播与助推日志完整性。 |
| [liveops/workspace.py](</Users/matchalee/Desktop/IDN Workflow/liveops/workspace.py>) | 扫描完成任务，更新运营工作台网页，让用户进入三类任务的最新报告。 |
| [requirements.txt](</Users/matchalee/Desktop/IDN Workflow/requirements.txt>) | 固定 Python 依赖版本；当前声明 SQLGlot，供安装和 SQL 语法树检查使用。 |
| [skills/anomaly-monitoring/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/anomaly-monitoring/SKILL.md>) | 指导复核规则提醒、日期、样本与零基线；需要时转下钻，保留无法判断状态。 |
| [skills/business-kpi-analysis/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/business-kpi-analysis/SKILL.md>) | 指导指标问数：读取口径与逻辑表结构、准备范围、写 SQL 并通过只读工具执行。 |
| [skills/business-kpi-analysis/references/metric_dictionary.md](</Users/matchalee/Desktop/IDN Workflow/skills/business-kpi-analysis/references/metric_dictionary.md>) | 指标知识的导航入口，指向 knowledge 中的统一定义，避免维护两套口径。 |
| [skills/business-report-writing/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/business-report-writing/SKILL.md>) | 指导汇总同次运行的证据，导出报告与清单，生成未发送的待推送包。 |
| [skills/campaign-review/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/campaign-review/SKILL.md>) | 指导活动复盘：固定活动名单、等长窗口比较、解释变化并导出。 |
| [skills/data-quality-check/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/data-quality-check/SKILL.md>) | 指导检查快照范围、主键关联、日期覆盖与支付对账；质量失败时停止后续分析。 |
| [skills/root-cause-drilldown/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/root-cause-drilldown/SKILL.md>) | 指导根据已有变化选择相关层级或主播追加聚合 SQL，区分事实、假设和缺失证据。 |
| [skills/streamer-traffic-boost/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/streamer-traffic-boost/SKILL.md>) | 指导助推更新：读取统一规则，查询完整主播清单，核对额度差值并导出待审核 CSV。 |
| [skills/weekly-report-update/SKILL.md](</Users/matchalee/Desktop/IDN Workflow/skills/weekly-report-update/SKILL.md>) | 指导 Agent 更新周报，检查整体与层级告警，按结果决定下钻并完成交付。 |
| [tests/test_agent_sql.py](</Users/matchalee/Desktop/IDN Workflow/tests/test_agent_sql.py>) | 开发验证：动态 SQL 计算、访问限制、结果契约、任务范围、证据导出和计划重放。 |
| [tests/test_validation.py](</Users/matchalee/Desktop/IDN Workflow/tests/test_validation.py>) | 开发验证：公共日期与范围校验、质量门禁、配置失效、只读连接、快照不覆盖和命令行入口。 |
| [印尼workflow方案.md](</Users/matchalee/Desktop/IDN Workflow/印尼workflow方案.md>) | 原始需求和历史设计，用来理解背景；其中的设想不等于当前已实现功能。 |

## 数据文件

当前默认读取 `data/operations-v2/liveops.sqlite`。数据根目录中的旧版文件保留为历史存档。以下只说明表结构与用途，不展示用户明细。

| 文件 | 大致内容与用途 |
| --- | --- |
| [data/liveops.sqlite](</Users/matchalee/Desktop/IDN Workflow/data/liveops.sqlite>) | 历史旧版快照，当前默认工具不使用。本地 SQLite 合成数据快照；当前工具实际从数据库查询，CSV 是便于查看的对应导出。 |
| [data/manifest.json](</Users/matchalee/Desktop/IDN Workflow/data/manifest.json>) | 历史旧版快照，当前默认工具不使用。合成快照说明：日期覆盖、业务时区、生成版本、快照标识和表规模，供核对数据来源。 |
| [data/operations-v2/campaign_streamers.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/campaign_streamers.csv>) | 当前默认运营快照。活动与主播名单的对应关系，用于保证前后比较使用同一名单。 |
| [data/operations-v2/campaigns.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/campaigns.csv>) | 当前默认运营快照。活动配置，包含活动 ID、名称与起止日期，用于准备活动分析窗口。 |
| [data/operations-v2/liveops.sqlite](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/liveops.sqlite>) | 当前默认运营快照。本地 SQLite 合成数据快照；当前工具实际从数据库查询，CSV 是便于查看的对应导出。 |
| [data/operations-v2/manifest.json](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/manifest.json>) | 当前默认运营快照。合成快照说明：日期覆盖、业务时区、生成版本、快照标识和表规模，供核对数据来源。 |
| [data/operations-v2/payment_attempts.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/payment_attempts.csv>) | 当前默认运营快照。支付尝试源数据，包含成功或失败状态及金额，主要用于当前支付对账检查。 |
| [data/operations-v2/streamer_daily.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/streamer_daily.csv>) | 当前默认运营快照。单主播单日实际开播秒数，含不开播零记录，用于直播时长、有效天数与完整性检查。 |
| [data/operations-v2/streamers.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/streamers.csv>) | 当前默认运营快照。合成主播维度，包含主播标识、层级和内容类别，用于筛选与分组。 |
| [data/operations-v2/traffic_boost_daily.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/traffic_boost_daily.csv>) | 当前默认运营快照。单主播单日历史实际助推额度，用于与建议额度比较；不是下发指令。 |
| [data/operations-v2/transactions.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/transactions.csv>) | 当前默认运营快照。成功交易源数据，包含金额及关联支付尝试，用于打赏金额与对账。 |
| [data/operations-v2/users.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/users.csv>) | 当前默认运营快照。合成用户维度，包含用户标识、平台、渠道和设备字段；用于源数据关联与质量校验，不向用户输出用户明细。 |
| [data/operations-v2/view_sessions.csv](</Users/matchalee/Desktop/IDN Workflow/data/operations-v2/view_sessions.csv>) | 当前默认运营快照。观看会话源数据，包含日期、观看双方标识和时长，用于计算观看时长与期间去重 UV。 |
| [data/payment_attempts.csv](</Users/matchalee/Desktop/IDN Workflow/data/payment_attempts.csv>) | 历史旧版快照，当前默认工具不使用。支付尝试源数据，包含成功或失败状态及金额，主要用于当前支付对账检查。 |
| [data/streamers.csv](</Users/matchalee/Desktop/IDN Workflow/data/streamers.csv>) | 历史旧版快照，当前默认工具不使用。合成主播维度，包含主播标识、层级和内容类别，用于筛选与分组。 |
| [data/transactions.csv](</Users/matchalee/Desktop/IDN Workflow/data/transactions.csv>) | 历史旧版快照，当前默认工具不使用。成功交易源数据，包含金额及关联支付尝试，用于打赏金额与对账。 |
| [data/users.csv](</Users/matchalee/Desktop/IDN Workflow/data/users.csv>) | 历史旧版快照，当前默认工具不使用。合成用户维度，包含用户标识、平台、渠道和设备字段；用于源数据关联与质量校验，不向用户输出用户明细。 |
| [data/view_sessions.csv](</Users/matchalee/Desktop/IDN Workflow/data/view_sessions.csv>) | 历史旧版快照，当前默认工具不使用。观看会话源数据，包含日期、观看双方标识和时长，用于计算观看时长与期间去重 UV。 |

## 工作台与历史参数

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/operations/index.html](</Users/matchalee/Desktop/IDN Workflow/outputs/operations/index.html>) | 运营工作台网页；提供周报、活动复盘和主播助推报告导航。 |
| [outputs/payment-report-args.json](</Users/matchalee/Desktop/IDN Workflow/outputs/payment-report-args.json>) | 旧支付诊断报告导出的参数和定性备注，引用历史证据；当前不作为新任务模板。 |

## 每次运行的产物

`sql-*-demo` 是当前动态 SQL 计划演示；`operations-*-demo`、`operations-*-v2` 和旧支付/风险目录保留历史记录。历史文件存在不代表旧工具仍可调用，也不代表已用当前知识重新验证。证据编号仅在所属 run 中有意义。

### demo-payment-20261015

用途：旧版支付诊断演示存档。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/demo-payment-20261015/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/demo-payment-20261015/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/e0002.json>) | get_metric_dictionary：读取当时的指标字典或知识契约；保存当次调用参数、状态与证据。 |
| [outputs/runs/demo-payment-20261015/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/e0003.json>) | check_data_quality：记录源数据质量检查；保存当次调用参数、状态与证据。 |
| [outputs/runs/demo-payment-20261015/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/e0004.json>) | query_kpis：旧版指标分析记录；保存当次调用参数、状态与证据。 |
| [outputs/runs/demo-payment-20261015/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/e0005.json>) | detect_anomalies：旧版异常监控记录；保存当次调用参数、状态与证据。 |
| [outputs/runs/demo-payment-20261015/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/e0006.json>) | get_dimension_breakdown：旧版维度下钻记录；保存当次调用参数、状态与证据。 |
| [outputs/runs/demo-payment-20261015/e0007.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/e0007.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/demo-payment-20261015/report-c5c634e8d765/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/report-c5c634e8d765/e0003.json>) | check_data_quality：记录源数据质量检查；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/demo-payment-20261015/report-c5c634e8d765/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/report-c5c634e8d765/e0004.json>) | query_kpis：旧版指标分析记录；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/demo-payment-20261015/report-c5c634e8d765/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/report-c5c634e8d765/e0005.json>) | detect_anomalies：旧版异常监控记录；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/demo-payment-20261015/report-c5c634e8d765/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/report-c5c634e8d765/e0006.json>) | get_dimension_breakdown：旧版维度下钻记录；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/demo-payment-20261015/report-c5c634e8d765/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/report-c5c634e8d765/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/demo-payment-20261015/report-c5c634e8d765/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/report-c5c634e8d765/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/demo-payment-20261015/report-c5c634e8d765/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-payment-20261015/report-c5c634e8d765/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |

### demo-risk-20261013

用途：旧版风险规则分析存档。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/demo-risk-20261013/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-risk-20261013/e0001.json>) | segment_audience：历史工具调用记录，现有工具目录不再提供该旧入口；保存当次调用参数、状态与证据。 |

### demo-unknown-metric

用途：旧版未知指标处理记录。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/demo-unknown-metric/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/demo-unknown-metric/e0001.json>) | query_kpis：旧版指标分析记录；保存当次调用参数、状态与证据。 |

### fixed-query-demo

用途：固定打赏查询演示。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/fixed-query-demo/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/fixed-query-demo/e0001.json>) | query_gift_total：记录固定打赏金额查询；保存当次调用参数、状态与证据。 |

### operations-boost-demo

用途：旧固定运营流程的助推演示存档。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/operations-boost-demo/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/operations-boost-demo/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-boost-demo/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/e0002.json>) | update_traffic_boost：历史工具调用记录，现有工具目录不再提供该旧入口；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-boost-demo/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/e0003.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-boost-demo/report-f744d7497dc9/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/report-f744d7497dc9/e0002.json>) | update_traffic_boost：历史工具调用记录，现有工具目录不再提供该旧入口；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/operations-boost-demo/report-f744d7497dc9/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/report-f744d7497dc9/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/operations-boost-demo/report-f744d7497dc9/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/report-f744d7497dc9/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/operations-boost-demo/report-f744d7497dc9/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/report-f744d7497dc9/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/operations-boost-demo/report-f744d7497dc9/traffic_boost_candidates.csv](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/report-f744d7497dc9/traffic_boost_candidates.csv>) | 待审核主播助推建议，包含指标、资格、旧额度、建议额度、差值与操作；不会实际下发。 |
| [outputs/runs/operations-boost-demo/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-demo/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### operations-boost-v2

用途：旧固定运营流程的助推迭代存档。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/operations-boost-v2/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/operations-boost-v2/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-boost-v2/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/e0002.json>) | update_traffic_boost：历史工具调用记录，现有工具目录不再提供该旧入口；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-boost-v2/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/e0003.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-boost-v2/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/e0004.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-boost-v2/report-515db704f673/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/report-515db704f673/e0002.json>) | update_traffic_boost：历史工具调用记录，现有工具目录不再提供该旧入口；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/operations-boost-v2/report-515db704f673/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/report-515db704f673/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/operations-boost-v2/report-515db704f673/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/report-515db704f673/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/operations-boost-v2/report-515db704f673/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/report-515db704f673/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/operations-boost-v2/report-515db704f673/traffic_boost_candidates.csv](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/report-515db704f673/traffic_boost_candidates.csv>) | 待审核主播助推建议，包含指标、资格、旧额度、建议额度、差值与操作；不会实际下发。 |
| [outputs/runs/operations-boost-v2/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-boost-v2/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### operations-campaign-demo

用途：旧固定运营流程的活动复盘存档。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/operations-campaign-demo/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/operations-campaign-demo/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-campaign-demo/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/e0002.json>) | review_campaign：历史工具调用记录，现有工具目录不再提供该旧入口；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-campaign-demo/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/e0003.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-campaign-demo/report-1629e62df99b/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/report-1629e62df99b/e0002.json>) | review_campaign：历史工具调用记录，现有工具目录不再提供该旧入口；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/operations-campaign-demo/report-1629e62df99b/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/report-1629e62df99b/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/operations-campaign-demo/report-1629e62df99b/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/report-1629e62df99b/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/operations-campaign-demo/report-1629e62df99b/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/report-1629e62df99b/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/operations-campaign-demo/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-demo/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### operations-campaign-v2

用途：旧固定运营流程的活动复盘迭代存档。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/operations-campaign-v2/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/operations-campaign-v2/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-campaign-v2/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/e0002.json>) | review_campaign：历史工具调用记录，现有工具目录不再提供该旧入口；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-campaign-v2/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/e0003.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-campaign-v2/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/e0004.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-campaign-v2/report-627ae5120d22/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/report-627ae5120d22/e0002.json>) | review_campaign：历史工具调用记录，现有工具目录不再提供该旧入口；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/operations-campaign-v2/report-627ae5120d22/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/report-627ae5120d22/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/operations-campaign-v2/report-627ae5120d22/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/report-627ae5120d22/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/operations-campaign-v2/report-627ae5120d22/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/report-627ae5120d22/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/operations-campaign-v2/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-campaign-v2/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### operations-weekly-demo

用途：旧固定运营流程的周报演示存档。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/operations-weekly-demo/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/operations-weekly-demo/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-weekly-demo/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/e0002.json>) | update_weekly_report：历史工具调用记录，现有工具目录不再提供该旧入口；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-weekly-demo/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/e0003.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-weekly-demo/report-537687574b62/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/report-537687574b62/e0002.json>) | update_weekly_report：历史工具调用记录，现有工具目录不再提供该旧入口；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/operations-weekly-demo/report-537687574b62/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/report-537687574b62/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/operations-weekly-demo/report-537687574b62/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/report-537687574b62/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/operations-weekly-demo/report-537687574b62/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/report-537687574b62/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/operations-weekly-demo/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-demo/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### operations-weekly-v2

用途：旧固定运营流程的周报迭代存档。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/operations-weekly-v2/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/operations-weekly-v2/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-weekly-v2/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/e0002.json>) | update_weekly_report：历史工具调用记录，现有工具目录不再提供该旧入口；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-weekly-v2/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/e0003.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-weekly-v2/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/e0004.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/operations-weekly-v2/report-24a4a35e270f/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/report-24a4a35e270f/e0002.json>) | update_weekly_report：历史工具调用记录，现有工具目录不再提供该旧入口；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/operations-weekly-v2/report-24a4a35e270f/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/report-24a4a35e270f/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/operations-weekly-v2/report-24a4a35e270f/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/report-24a4a35e270f/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/operations-weekly-v2/report-24a4a35e270f/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/report-24a4a35e270f/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/operations-weekly-v2/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/operations-weekly-v2/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### smoke

用途：运行记录。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/smoke/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/smoke/e0001.json>) | query_kpis：旧版指标分析记录；保存当次调用参数、状态与证据。 |

### sql-boost-demo

用途：当前 SQL 计划方式的主播助推演示。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/sql-boost-demo/agent_plan.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/agent_plan.json>) | 本次重放保存的原始 Agent SQL 计划副本。 |
| [outputs/runs/sql-boost-demo/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/sql-boost-demo/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-boost-demo/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/e0002.json>) | read_business_knowledge：读取任务口径、结构、规则与知识版本；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-boost-demo/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/e0003.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-boost-demo/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/e0004.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：近七天运营指标；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-boost-demo/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/e0005.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：助推更新待审核清单；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-boost-demo/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/e0006.json>) | assemble_analysis：汇总本任务查询及引用关系；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-boost-demo/e0007.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/e0007.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-boost-demo/e0008.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/e0008.json>) | prepare_delivery：记录待推送包、流程状态与工作台更新；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-boost-demo/plan_request.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/plan_request.json>) | 保存计划、读取后的 SQL、知识版本、快照标识及请求指纹，用于识别同一重放请求。 |
| [outputs/runs/sql-boost-demo/report-70ea255eb4e0/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/report-70ea255eb4e0/e0003.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-boost-demo/report-70ea255eb4e0/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/report-70ea255eb4e0/e0004.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：近七天运营指标；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-boost-demo/report-70ea255eb4e0/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/report-70ea255eb4e0/e0005.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：助推更新待审核清单；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-boost-demo/report-70ea255eb4e0/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/report-70ea255eb4e0/e0006.json>) | assemble_analysis：汇总本任务查询及引用关系；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-boost-demo/report-70ea255eb4e0/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/report-70ea255eb4e0/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/sql-boost-demo/report-70ea255eb4e0/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/report-70ea255eb4e0/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/sql-boost-demo/report-70ea255eb4e0/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/report-70ea255eb4e0/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/sql-boost-demo/report-70ea255eb4e0/traffic_boost_candidates.csv](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/report-70ea255eb4e0/traffic_boost_candidates.csv>) | 待审核主播助推建议，包含指标、资格、旧额度、建议额度、差值与操作；不会实际下发。 |
| [outputs/runs/sql-boost-demo/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-boost-demo/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### sql-campaign-demo

用途：当前 SQL 计划方式的活动复盘演示。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/sql-campaign-demo/agent_plan.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/agent_plan.json>) | 本次重放保存的原始 Agent SQL 计划副本。 |
| [outputs/runs/sql-campaign-demo/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/sql-campaign-demo/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-campaign-demo/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/e0002.json>) | read_business_knowledge：读取任务口径、结构、规则与知识版本；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-campaign-demo/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/e0003.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-campaign-demo/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/e0004.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：活动名单本期指标；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-campaign-demo/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/e0005.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：同名单活动前后对比；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-campaign-demo/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/e0006.json>) | assemble_analysis：汇总本任务查询及引用关系；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-campaign-demo/e0007.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/e0007.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-campaign-demo/e0008.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/e0008.json>) | prepare_delivery：记录待推送包、流程状态与工作台更新；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-campaign-demo/plan_request.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/plan_request.json>) | 保存计划、读取后的 SQL、知识版本、快照标识及请求指纹，用于识别同一重放请求。 |
| [outputs/runs/sql-campaign-demo/report-06148b3f2e60/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/report-06148b3f2e60/e0003.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-campaign-demo/report-06148b3f2e60/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/report-06148b3f2e60/e0004.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：活动名单本期指标；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-campaign-demo/report-06148b3f2e60/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/report-06148b3f2e60/e0005.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：同名单活动前后对比；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-campaign-demo/report-06148b3f2e60/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/report-06148b3f2e60/e0006.json>) | assemble_analysis：汇总本任务查询及引用关系；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-campaign-demo/report-06148b3f2e60/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/report-06148b3f2e60/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/sql-campaign-demo/report-06148b3f2e60/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/report-06148b3f2e60/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/sql-campaign-demo/report-06148b3f2e60/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/report-06148b3f2e60/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/sql-campaign-demo/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-campaign-demo/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### sql-dev-check

用途：运行记录。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/sql-dev-check/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check/e0001.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check/e0002.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；保存当次调用参数、状态与证据。 |

### sql-dev-check-2

用途：运行记录。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/sql-dev-check-2/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/sql-dev-check-2/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/e0001.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check-2/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/e0002.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check-2/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/e0003.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check-2/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/e0004.json>) | assemble_analysis：汇总本任务查询及引用关系；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check-2/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/e0005.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check-2/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/e0006.json>) | prepare_delivery：记录待推送包、流程状态与工作台更新；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check-2/e0007.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/e0007.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check-2/e0008.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/e0008.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-dev-check-2/report-53ef38e793bf/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/report-53ef38e793bf/e0001.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-dev-check-2/report-53ef38e793bf/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/report-53ef38e793bf/e0002.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-dev-check-2/report-53ef38e793bf/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/report-53ef38e793bf/e0003.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-dev-check-2/report-53ef38e793bf/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/report-53ef38e793bf/e0004.json>) | assemble_analysis：汇总本任务查询及引用关系；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-dev-check-2/report-53ef38e793bf/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/report-53ef38e793bf/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/sql-dev-check-2/report-53ef38e793bf/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/report-53ef38e793bf/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/sql-dev-check-2/report-53ef38e793bf/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/report-53ef38e793bf/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/sql-dev-check-2/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-dev-check-2/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

### sql-weekly-demo

用途：当前 SQL 计划方式的周报演示。

| 文件 | 大致内容与用途 |
| --- | --- |
| [outputs/runs/sql-weekly-demo/agent_plan.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/agent_plan.json>) | 本次重放保存的原始 Agent SQL 计划副本。 |
| [outputs/runs/sql-weekly-demo/delivery_draft.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/delivery_draft.json>) | 未发送的待推送草稿，保存任务标题、日期与产物位置；不会自行发送。 |
| [outputs/runs/sql-weekly-demo/e0001.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0001.json>) | get_data_profile：确认快照日期范围、业务时区与可用活动；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/e0002.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0002.json>) | read_business_knowledge：读取任务口径、结构、规则与知识版本；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0003.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0004.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：本期五项核心指标；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0005.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：整体与层级周期对比；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0006.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：尾部主播观看表现下钻；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/e0007.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0007.json>) | assemble_analysis：汇总本任务查询及引用关系；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/e0008.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0008.json>) | export_report：记录报告导出及生成文件路径；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/e0009.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/e0009.json>) | prepare_delivery：记录待推送包、流程状态与工作台更新；保存当次调用参数、状态与证据。 |
| [outputs/runs/sql-weekly-demo/plan_request.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/plan_request.json>) | 保存计划、读取后的 SQL、知识版本、快照标识及请求指纹，用于识别同一重放请求。 |
| [outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0003.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0003.json>) | prepare_analysis：记录固定的日期窗口、主播范围和所需结果；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0004.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0004.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：本期五项核心指标；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0005.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0005.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：整体与层级周期对比；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0006.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0006.json>) | execute_readonly_sql：记录提交 SQL、实际执行 SQL、绑定参数与聚合结果；补充查询标签：尾部主播观看表现下钻；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0007.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/e0007.json>) | assemble_analysis：汇总本任务查询及引用关系；为报告目录内复制的证据，便于随报告追溯。 |
| [outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/report.html](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/report.html>) | 浏览器可打开的报告看板，展示指标、比较、说明及证据链接。 |
| [outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/report.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/report.json>) | 机器可读报告，保存所引用的工具证据和 Agent 备注等信息。 |
| [outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/report.md](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/report-6a6ccf5f1767/report.md>) | 便于阅读、复制和编辑的 Markdown 报告。 |
| [outputs/runs/sql-weekly-demo/workflow_state.json](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/sql-weekly-demo/workflow_state.json>) | 任务完成状态、任务类型、版本及报告路径；供工作台选择报告。 |

## 发现链接与环境文件

| 路径 | 用处 |
| --- | --- |
| `.agents/skills/anomaly-monitoring` | 符号链接，指向 `skills/anomaly-monitoring`；让 Agent 发现 Skill，实际只维护目标目录。 |
| `.agents/skills/business-kpi-analysis` | 符号链接，指向 `skills/business-kpi-analysis`；让 Agent 发现 Skill，实际只维护目标目录。 |
| `.agents/skills/business-report-writing` | 符号链接，指向 `skills/business-report-writing`；让 Agent 发现 Skill，实际只维护目标目录。 |
| `.agents/skills/campaign-review` | 符号链接，指向 `skills/campaign-review`；让 Agent 发现 Skill，实际只维护目标目录。 |
| `.agents/skills/data-quality-check` | 符号链接，指向 `skills/data-quality-check`；让 Agent 发现 Skill，实际只维护目标目录。 |
| `.agents/skills/root-cause-drilldown` | 符号链接，指向 `skills/root-cause-drilldown`；让 Agent 发现 Skill，实际只维护目标目录。 |
| `.agents/skills/streamer-traffic-boost` | 符号链接，指向 `skills/streamer-traffic-boost`；让 Agent 发现 Skill，实际只维护目标目录。 |
| `.agents/skills/weekly-report-update` | 符号链接，指向 `skills/weekly-report-update`；让 Agent 发现 Skill，实际只维护目标目录。 |
| `.venv/` | 项目 Python 虚拟环境和安装的依赖；属于运行环境，不逐个列第三方文件。 |
| `.git/` | Git 版本管理内部记录；不属于业务源码，不逐个列内部文件。 |
| `**/__pycache__/`、`*.pyc` | Python 自动生成的字节码缓存；无需手动维护。 |

## 通常需要修改哪里

- 改指标定义：先看 `knowledge/metrics.json`，同时核对规则、SQL 与相关验证。
- 改数据字段或接入：先看 `knowledge/schema.json`、`liveops/sql_guard.py`、`liveops/store.py` 和质量检查；真实数据库接入需要整体适配。
- 改阈值或额度：改 `config/operations_metrics.json`；使用新 run_id 重新查询。
- 改 Agent 的任务步骤：改 `skills/` 下对应 Skill。
- 改查询计算：由 Agent 按口径写 SQL；核对后可沉淀到 `knowledge/sql_examples/`。
- 改固定重放顺序：改具体 JSON 计划；`SQL_PLAN_FORMAT.md` 用来查格式。
- 改报告样式：看 `liveops/report.py`；改工作台导航看 `liveops/workspace.py`。
- 查一次分析怎么得出：进入对应 `outputs/runs/<run_id>/`，从计划和 `e*.json` 追踪到报告。
