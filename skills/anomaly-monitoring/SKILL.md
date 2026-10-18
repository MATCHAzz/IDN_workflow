---
name: anomaly-monitoring
description: Review SQL-produced LiveOps alerts against the knowledge-defined baseline, sample and threshold rules, and route confirmed changes to focused drilldown.
---

# 告警复核

从周报/活动转入时复用已有比较SQL结果，不重新运行整套查询，也不返回周报Skill形成循环。读取[规则知识](../../knowledge/rules.md)及read_business_knowledge返回的实际阈值，核对整体与层级、日期、样本量、名单和knowledge_id。

比较结果应由Agent生成的SQL计算delta/relative_change/is_anomaly/status；零基线和小样本为NULL，不能解释为正常。发现SQL用错口径时修改SQL后重新执行，不用文字直接改数值。已确认规则提醒时读[root-cause-drilldown](../root-cause-drilldown/SKILL.md)，已有证据足够则停止。

只读与结果契约校验不自动证明业务规则正确。针对新问题可以改写SQL，但不能临时改业务定义或把前后变化称因果。
