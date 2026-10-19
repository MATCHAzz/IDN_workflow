# LiveOps：Skills + 业务知识库 + Agent写SQL

用于周报更新、活动复盘和主播流量助推更新。**Skills定义任务步骤，文件知识库保存口径与表结构，当前项目Agent根据问题编写SQL，数据库工具执行，固定程序导出报告和看板。**

核心指标：打赏金额、看播时长、有效直播天数、直播时长、观看观众数。使用合成SQLite数据；未接真实内部系统、定时器、消息渠道或实际流量下发。

接手项目请先看[项目交接文档](</Users/matchalee/Desktop/IDN Workflow/HANDOFF.md>)，其中说明当前状态、已完成内容、未完成事项和运行入口。

## 直接体验

在当前项目聊天发送：

> 根据业务知识库更新截至2026-10-17的周报，展示所用SQL，发现异常时按需要下钻并生成看板。

> 复盘印尼腰尾主播任务活动，保持同主播名单，对比活动前后五项指标。

> 根据知识库规则更新2026-10-17助推名单，生成待审核CSV。

[打开运营工作台](outputs/operations/index.html)。页面是结果导航，聊天入口仍是当前项目Agent；没有用关键词脚本模拟模型。

## 安装与入口

Python>=3.10。在项目根目录：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m liveops tools
```

SQLGlot用于SQL语法树和来源检查。其余运行逻辑使用标准库。已附data/operations-v2/合成快照；没有数据时运行`.venv/bin/python -m liveops init`，不会覆盖已有快照。

## 保留的最简单固定查询

[liveops/simple_query.py](liveops/simple_query.py)里只有一条业务SQL：查询指定日期范围的成功打赏金额。

```sh
.venv/bin/python -m liveops.simple_query --start-date 2026-10-11 --end-date 2026-10-17
```

固定查询便于学习和对照；周报/复盘/助推由Agent编写SQL。数据库连接、元数据读取、质量检查、范围限制和结果验证仍由代码确定性执行，这些基础设施查询不算临时业务分析。

## 知识与动态SQL

| 位置 | 用途 |
| --- | --- |
| knowledge/routes.json | 各任务的共同必读与专用知识映射 |
| knowledge/catalog.json | 知识ID、别名、标签、适用范围、原文定位与关联依赖 |
| knowledge/metrics.json | 指标定义、单位、聚合与空值口径 |
| knowledge/schema.json | 允许使用的数据源、字段、粒度和关联 |
| knowledge/rules.md | 周报、活动、助推与提醒规则 |
| knowledge/sql_examples/ | 已执行核对的SQL参考；Agent可按任务修改 |
| config/operations_metrics.json | 唯一阈值来源，随知识读取返回 |
| skills/ | 任务指引；.agents/skills/是发现链接 |

Agent先get_data_profile、read_business_knowledge、prepare_analysis，再把写好的SQL交execute_readonly_sql。需要时查看结果继续下钻；最后assemble_analysis、export_report、prepare_delivery。所有步骤复用run_id。参数通过--args-file传递，不把SQL直接拼进shell。

read_business_knowledge按topic实际选择规则与SQL参考，共同口径始终加载。需要查找知识时，search_business_knowledge按别名、标签和适用任务查目录，再通过entry_ids补读正文与依赖；例如“独立观众”对应metric.viewer_uv。返回条目位置和选择原因，所有主题仍共用全库knowledge_id。参数文件与维护方法见[知识路由说明](knowledge/README.md)。

业务知识不负责执行数据库；工具也不根据自然语言自动挑模板。数据查询实际使用SQLite方言，接Hive时需要真实只读连接器及方言适配，当前没有假装接上内部库。

## SQL计划重放

Agent编写的SQL可保存成JSON计划，便于查看与重放：[格式说明](docs/SQL_PLAN_FORMAT.md)。

```sh
.venv/bin/python -m liveops run-plan --plan-file examples/sql_plans/weekly_report.json
.venv/bin/python -m liveops run-plan --plan-file examples/sql_plans/campaign_review.json
.venv/bin/python -m liveops run-plan --plan-file examples/sql_plans/traffic_boost_update.json
```

这些文件是明确保存的示例计划，命令不调用模型，也不能替代Agent的自然语言理解与动态决策。only_if_alerts只能按已有结果执行计划中的条件查询。日常新问题仍由当前Agent读知识、写SQL和选择下一步。

## 执行边界与追溯

SQL入口接受单条SELECT/非递归WITH，限定逻辑数据源，自动注入日期与主播范围，使用只读连接、表/函数权限、超时和结果行数上限。viewer_id仅允许去重计数，不能返回用户明细。多个明细事实表直接JOIN会拒绝，需先聚合。

这些检查不自动证明业务语义正确，Agent还需核对粒度、关联、单位与勾稽关系。已验证SQL示例用独立查询核对后沉淀，不把“执行成功”当正确性证明。实现参考[SQLGlot](https://github.com/tobymao/sqlglot)和[SQLite授权回调](https://www.sqlite.org/c3ref/set_authorizer.html)。

知识/配置改变会改变knowledge_id；不能把旧证据混入新报告。outputs/runs/每个run保存Agent SQL、实际限定后的SQL、参数、结果、SQL计划、报告与待推送包。相同run_id的同计划重放复用已完成结果；失败或输入变更使用新ID。

内部数据与定时推送未接入，delivery_draft.json未发送；助推CSV不实际下发；用户经历中的工时节约不是本Demo实测结果。

## 当前代码

新路径：knowledge.py读知识；sql_guard.py检查SQL；sql_tools.py暴露工具；sql_analysis.py准备上下文并校验/汇总；plan_runner.py重放计划；report.py生成看板。

validation.py保存共用质量与范围校验；workspace.py生成结果导航；ops_mock.py生成当前合成快照。旧支付诊断、人群分层和固定业务流程脚本及legacy-workflow入口已移除。已有数据和历史报告保留。

验证：`.venv/bin/python -m unittest discover -s tests -v`。详细流程见[当前说明](docs/OPERATIONS_WORKFLOW.md)。
