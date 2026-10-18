---
name: weekly-report-update
description: Update the LiveOps weekly report by reading business knowledge, authoring and executing SQL, checking overall and tier alerts, investigating relevant changes and exporting evidence-backed reports.
---

# 周报更新

1. 用get_data_profile核对日期；调用read_business_knowledge(topic=weekly_report)，读取[指标与表结构](../../knowledge/README.md)及适用SQL示例。运行`.venv/bin/python -m liveops call TOOL --run-id <本任务ID> --args-file <JSON文件>`。
2. 调prepare_analysis，传workflow=weekly_report、report_date，可选streamer_tier。复用返回的计划evidence_id和knowledge_id，不自行更换基线窗口。
3. **由Agent编写SQL**：本期查询result_kind=metrics、window=current，整体dimension='all'、五项指标；对比查询result_kind=comparison、window=comparison，比较整体与主播层级。可参考period_metrics.sql和period_comparison.sql，不必重新发明标准口径，也不能把自动套模板说成模型写SQL。
4. 调execute_readonly_sql，传计划ID、知识ID、SQL、result_kind/window和label。结果或质量失败则停止。核对期间UV、看播/开播时长、有效主播日以及JOIN粒度；必要时追加聚合对照SQL。通过语法/只读检查不代表业务计算已获证明。

## 按结果分支

| 比较结果 | 下一步 |
| --- | --- |
| 整体或任一层级is_anomaly=1/true | 必须读[anomaly-monitoring](../anomaly-monitoring/SKILL.md)，复核日期、名单、样本和基线，再读[root-cause-drilldown](../root-cause-drilldown/SKILL.md)。先用已有层级证据；不足时由Agent编写相关主播/层级SQL继续查询，不无条件重查全部指标。 |
| 比较非空、全部0/false且status=ok | 常规周报，写“未触发当前规则”，不强行调查。 |
| 无true但有null、非ok或缺结果 | 说明无法判断的原因，按需读取监控Skill，只报告可靠事实。 |

告警与不确定同时存在时分别保留。证据足够就停止，事实、可能解释和验证缺口分开；不声称因果。

5. 按[报告Skill](../business-report-writing/SKILL.md)调用assemble_analysis、export_report、prepare_delivery。只交付实际产物，不主动罗列样例数字和测试数量。
6. 如需复现，将自己编写的SQL保存为[计划文件](../../docs/SQL_PLAN_FORMAT.md)，用run-plan重放。该命令不理解自然语言，不替代Agent的分析决策。固定周报旧命令已移除。
