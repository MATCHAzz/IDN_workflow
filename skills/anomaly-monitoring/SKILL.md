---
name: anomaly-monitoring
description: Review SQL-produced LiveOps alerts against the knowledge-defined baseline, sample and threshold rules, and route confirmed changes to focused drilldown.
---

# 告警复核

从周报/活动转入时复用已有比较SQL结果，不重新运行整套查询，也不返回周报Skill形成循环。同run调用read_business_knowledge(topic=anomaly_monitoring)补读[监控知识](../../knowledge/README.md)和实际阈值；按需指定entry_ids补读目录条目。补读主题不改变原分析计划或全库knowledge_id，核对整体与层级、日期、样本量、名单和版本。

比较结果应由Agent生成的SQL计算delta/relative_change/is_anomaly/status；零基线和小样本为NULL，不能解释为正常。发现SQL用错口径时修改SQL后重新执行，不用文字直接改数值。已确认规则提醒时读[root-cause-drilldown](../root-cause-drilldown/SKILL.md)，已有证据足够则停止。

只读与结果契约校验不自动证明业务规则正确。针对新问题可以改写SQL，但不能临时改业务定义或把前后变化称因果。
