# LiveOps：Skills + 文件知识库 + Agent SQL

主线是周报更新、活动复盘和主播流量助推更新。五项核心指标：打赏金额、看播时长、有效直播天数、直播时长、观看观众数。自然语言入口为当前项目Agent；模型按Skills读取知识、编写SQL、选择下钻。用户明确不需要主动展示样例业务数字和测试通过数量；交付聚焦流程、产物和用法。

## 分析入口

1. 使用项目根目录`.venv/bin/python -m liveops tools`查看当前工具。默认数据data/operations-v2/；不存在时执行init，已有快照不覆盖。SQL执行需要requirements.txt中的SQLGlot，使用项目.venv。
2. 按任务读取相关SKILL.md。skills/存实际文件，.agents/skills/为发现链接，勿维护两份。
3. 调get_data_profile确认日期与活动。固定Asia/Jakarta；相对日期超出快照时说明，不静默换日。无必要参数时先确认数据范围，再澄清。
4. 调read_business_knowledge，读取knowledge/下指标、表结构、规则和适用SQL示例。以knowledge_id标识知识版本；知识库只是指引，不执行SQL。
5. 每个任务用新run_id，同任务所有调用复用。使用prepare_analysis确定周报/活动/助推的日期和名单，再由Agent写SQL，交execute_readonly_sql执行。SQL通过--args-file传递，避免拼接shell文本。

## Skills路由

| 问题 | 读取 |
| --- | --- |
| 周报 | skills/weekly-report-update/SKILL.md |
| 活动复盘 | skills/campaign-review/SKILL.md |
| 助推更新 | skills/streamer-traffic-boost/SKILL.md |
| 指标/SQL问数 | skills/business-kpi-analysis/SKILL.md |
| 质量/漏数 | skills/data-quality-check/SKILL.md |
| 提醒复核 | skills/anomaly-monitoring/SKILL.md |
| 下钻 | skills/root-cause-drilldown/SKILL.md |
| 报告与待推送包 | skills/business-report-writing/SKILL.md |

## 执行约束

- 业务SQL由Agent按知识库生成，可以改写示例。execute_readonly_sql只读执行，不从问题挑选模板、不替模型生成SQL。run-plan只重放已有SQL计划，不是独立聊天Agent。
- 只使用工具暴露的逻辑数据源，不能直接连接物理库、自写脚本绕过SQL检查或修改工具来完成普通问数。允许在outputs/保存SQL和参数文件，代码维护请求另按用户要求处理。
- 不输出用户明细；viewer_id仅可COUNT(DISTINCT viewer_id)。助推允许合成主播ID与聚合指标。多个明细事实表先各自聚合再JOIN，不能相加跨日/跨主播UV。
- Python仅保留query_gift_total作为默认可调用的固定业务查询例子。连接、元数据、质量检查、范围限制、结果验证和报告程序仍确定性执行；它们不代替业务SQL。旧支付诊断、人群分层和固定业务流程代码已删除，不调用历史工具。
- 质量失败停止分析与导出。执行成功不证明业务语义正确：Agent需核对粒度、关联、单位、日期、名单和勾稽关系；未知指标说明缺数据，不编造。
- SQL计算数值、差值与告警；Agent解释事实并选择下一次查询，不凭感觉修改口径。阈值取config/operations_metrics.json，知识库与配置版本一致。
- 周报同时检查整体和层级；任一告警读取监控与下钻Skills，无告警生成常规报告，null/小样本保留无法判断。下钻有足够证据就停止，不固定跑满所有维度。
- 完成后assemble_analysis汇总证据，export_report渲染，prepare_delivery保存待推送包并更新工作台。知识或数据改变后使用新run_id并重新查询，不能拼接旧证据。任务失败保留记录，不伪装成完成。
- 不读取ops_mock.py、tests/或原方案事件答案作业务证据。开发/测试任务可以读取。
- 真实内部系统、定时器、发送渠道与实际助推下发未接入；草稿不等于已发送。履历中近四小时节约不是Demo实测结果。不需要子Agent。

## 开发验证

Python>=3.10。安装：python3 -m venv .venv，然后.venv/bin/python -m pip install -r requirements.txt。验证：.venv/bin/python -m unittest discover -s tests -v。tests/test_agent_sql.py覆盖SQL流程，tests/test_validation.py覆盖公共校验；不再依赖已删除的旧业务实现。
