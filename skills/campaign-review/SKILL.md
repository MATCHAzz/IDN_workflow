---
name: campaign-review
description: Review a LiveOps campaign using business knowledge and Agent-authored SQL over a fixed streamer cohort and equal before/during windows, then export the results.
---

# 活动复盘

先get_data_profile确认活动ID，再read_business_knowledge(topic=campaign_review)，按[知识映射](../../knowledge/README.md)加载共同口径、活动和监控规则及期间SQL参考，检查routing和原文位置。不明确的指标可按目录别名/标签检索，再用entry_ids补读。调prepare_analysis(workflow=campaign_review,campaign_id=实际ID)，日期和冻结名单由活动配置确定，不另传report_date。

Agent根据口径编写本期metrics SQL及comparison SQL，使用execute_readonly_sql、同run计划ID和knowledge_id执行。示例period_metrics.sql和period_comparison.sql可复用结构并修改，数据库工具会将两期限定为同名单、等长窗口。不是由Python根据问句自动选模板。

检查整体与层级变化，异常时读取监控/下钻Skills并按需要写追加SQL。未知成本/退款/随机实验数据不能补估；前后变化不等于AB因果收益、真实毛利或ROI。

按报告Skill汇总、导出和生成待推送包；可保存Agent所写SQL计划用于run-plan重放。真实内部系统、定时推送未配置。用户未要求时不主动展示样例业务数字和测试数量。
