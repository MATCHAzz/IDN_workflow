# LiveOps 业务知识库

本目录保存业务知识，不执行查询。Agent先按任务读取知识，再根据问题编写SQL，通过execute_readonly_sql执行。知识路由不选择可执行SQL模板，也不代替Agent理解问题。

| 文件 | 内容 |
| --- | --- |
| routes.json | 任务到知识ID的显式映射；common为所有任务必读，其余按topic补充 |
| catalog.json | 知识目录：稳定ID、名称、别名、标签、适用任务、逻辑源、方言、正文位置与依赖 |
| metrics.json | 五项指标定义、单位、聚合与空值口径 |
| schema.json | 允许的逻辑数据源、字段、粒度与关联关系 |
| rules.md | 通用约束及周报、活动、助推、监控、下钻、质量和交付规则；目录按章节引用 |
| sql_examples/ | 经核对的SQL参考；Agent按任务修改，不由工具自动执行 |
| ../config/operations_metrics.json | 唯一阈值和配额来源，不在目录里复制数值 |

## 文件映射

read_business_knowledge(topic=...)加载routes.json中的共同必读和任务条目。共同部分包括五指标、聚合约束、完整表结构、配置、通用规则、结果契约和SQL使用说明。各任务再补充：

| topic | 专用知识 |
| --- | --- |
| metrics / ad_hoc | 期间五指标SQL参考；按具体问题补读 |
| weekly_report | 周报窗口、监控规则、期间指标与整体/层级比较SQL参考 |
| campaign_review | 冻结名单与等长窗口规则、监控规则、期间指标和比较SQL参考 |
| traffic_boost_update | 助推规则、期间指标与主播助推清单SQL参考 |
| data_quality_check | 质量规则 |
| anomaly_monitoring | 监控规则与比较SQL参考 |
| root_cause_drilldown | 下钻、监控规则与期间指标/比较SQL参考 |
| business_report_writing | 报告和待推送草稿规则 |

返回的routing说明所选主题和条目；knowledge_entries包含正文、原文位置、source_sha256和selection_reasons（common、topic、requested或dependency）。instructions及example_paths保留原接口字段，但只汇总本次选中的规则与SQL参考。metrics/schema/rules配置契约仍完整返回，避免遗漏共同口径。

## 目录、别名和标签

search_business_knowledge返回目录元数据，不读取正文到Agent上下文。无参数时列出完整目录；query按名称、ID、别名、标签和逻辑源做大小写/全角归一后的包含匹配，topic限定适用任务，tags要求全部匹配。

它是确定性目录查找，不是语义检索。Agent负责理解用户问题；没有匹配时查看目录或澄清，不能编造指标。若已知任务，直接read_business_knowledge即可，不必先检索。

例如“活动期间有多少独立观众”可命中metric.viewer_uv。Agent再调用read_business_knowledge(topic=campaign_review,entry_ids=["metric.viewer_uv"])，加载活动任务知识、UV定义及requires关联的聚合约束和表结构。

在项目根目录运行以下示例；同一任务的调用复用run_id，新任务换新ID：

```sh
.venv/bin/python -m liveops call read_business_knowledge --run-id knowledge-routing-example --args-file examples/knowledge/weekly_report.json
.venv/bin/python -m liveops call search_business_knowledge --run-id knowledge-catalog-example --args-file examples/knowledge/find_viewer_uv.json
.venv/bin/python -m liveops call read_business_knowledge --run-id knowledge-catalog-example --args-file examples/knowledge/read_viewer_uv.json
```

这些调用只读取知识并保存工具证据，不生成业务报告。遇到告警时可在原任务run中补读topic=anomaly_monitoring或root_cause_drilldown，原分析计划不变。

## 维护与版本

新增知识时先编写或完善原文，再在catalog.json加入条目，最后在routes.json指定适用任务。不复制原文到目录：source.path相对knowledge目录，JSON用pointer定位，Markdown用唯一二级heading定位；配置仅允许引用config/operations_metrics.json。标题或JSON结构变更时同步更新定位。

条目ID使用稳定名称，例如metric.viewer_uv；更改展示名称时保留ID。aliases用于同义表达，tags用于筛选，topics表示适用任务，sources是逻辑源名称，dialect为当前sqlite；requires定义需要一起读取的知识ID，自动递归补齐并去重。补读entry_ids允许跨任务，但不更改原分析计划的日期或名单。

映射、目录、正文、SQL参考及配置共同计算**全库knowledge_id**。切换主题、按标签查找、补读条目不会改变版本；其中任一文件实际修改后版本改变，旧证据不能混入新报告，需使用新run重新查询。读取时校验ID、依赖、文件、JSON位置与章节，缺失或循环则报错，不静默漏读。

当前未接入向量数据库、语义检索或自动技能进化。将来换Hive需适配连接器、目录方言和SQL参考。
