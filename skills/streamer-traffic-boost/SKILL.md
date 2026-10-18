---
name: streamer-traffic-boost
description: Prepare a reviewable streamer traffic-boost update list by reading the rules, writing SQL for recent metrics and prior allocations, and exporting a CSV without applying changes.
---

# 主播流量助推更新

get_data_profile确认日期，read_business_knowledge(topic=traffic_boost_update)读取[指标/规则/表结构](../../knowledge/README.md)，prepare_analysis(workflow=traffic_boost_update,report_date=日期)固定近七天范围。

Agent编写两条SQL：整体metrics与完整主播boost清单。参考period_metrics.sql、boost_candidates.sql，交execute_readonly_sql(result_kind=metrics/boost,window=current)执行；门槛、建议额度、昨日日期使用工具参数，不写另一套常数。不同问题可改SQL或追加聚合分析，不在Python中添加新的业务查询函数。

检查完整主播覆盖、有效天数、期间UV和额度差值。可输出执行任务需要的合成主播ID，不输出观看用户明细。建议规则是Demo配额，不是最优流量或营收预测。

按报告Skill汇总并导出CSV/看板/待推送包。CSV只待审核，不下发实际流量。支持保存SQL计划重放；用户未要求时不主动罗列样例数字或测试数量。
