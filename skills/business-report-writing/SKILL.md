---
name: business-report-writing
description: Assemble same-plan Agent SQL evidence, export an operations report and optional traffic CSV, and prepare an unsent delivery package with knowledge-version checks.
---

# 汇总与导出

完成查询、告警复核和必要下钻后，按同run执行：

1. assemble_analysis(plan_evidence_id,query_evidence_ids)：汇总本期整体五指标、比较或助推清单，以及补充聚合。完整任务所需结果见prepare_analysis.required_results。不能把固定查询或其他任务证据混进来。
2. export_report(date,evidence_ids=[汇总结果ID],notes=可选备注)：工具从SQL结果渲染数字，报告附实际SQL和参数证据；助推额外导出CSV。
3. prepare_delivery(analysis_evidence_id,report_evidence_id)：生成delivery_draft.json、workflow_state.json并更新工作台。仅导出报告不代表已生成待推送包。

notes支持observations/hypotheses/next_checks，每条为text和evidence_ids；只写引用证据的定性文字，不嵌入数字，避免数字与结果不一致。语义解释仍需人工审阅。

知识库、配置、快照、run和计划需一致，改变后重新查询；旧知识证据拒绝导出。报告为内部草稿，未接真实发送/调度。用户未要求时交付链接和用法即可，不主动罗列样例数字与测试数量。
