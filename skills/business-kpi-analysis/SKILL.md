---
name: business-kpi-analysis
description: Read the LiveOps metric and schema knowledge, write SQL for gift amount, watch time, effective broadcast days, live time and viewers, then execute it through the scoped read-only tool.
---

# 知识库驱动SQL问数

1. get_data_profile确认范围，read_business_knowledge读取[knowledge/](../../knowledge/README.md)。定义、字段、关联、去重和阈值从知识取，不靠猜。
2. 周报/活动/助推使用对应prepare_analysis计划。自定义日期问数用prepare_analysis(workflow=ad_hoc,start_date,end_date，可选streamer_tier/campaign_id)，Agent根据问题选择范围；单项追问也可复用同任务计划，result_kind=table。没有必要日期时先澄清，不能静默换时间。
3. Agent自己写SQLite SELECT/WITH，保存outputs下SQL与参数JSON。execute_readonly_sql需plan_evidence_id、knowledge_id、sql、window、result_kind。工具自动限定日期和主播范围，只暴露schema.json的逻辑源；不能查询物理表/用户明细。
4. 五项指标完整输出用metrics契约；补充聚合用table。查五项指标时可参考sql_examples，但需检查所选口径、粒度和单位。只有viewer_id的COUNT(DISTINCT)可用，不能相加每日UV。

保留的固定对照仅query_gift_total：指定start_date/end_date后由liveops/simple_query.py查询打赏金额。用户明确要求最简单固定查询或核对动态结果时可用，普通多指标分析使用Agent编写的SQL。

问完整周报/活动/助推时转对应任务Skill。未知指标、退款或费用信息不编造。执行成功不保证SQL业务语义正确，需对照知识和已验证示例复核。
