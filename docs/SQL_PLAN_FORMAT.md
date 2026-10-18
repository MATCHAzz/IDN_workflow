# Agent SQL计划格式

自然语言入口是当前项目Agent。Agent先读取Skills和knowledge/，自己编写SQL并查看执行结果；run-plan只重放已经写好的计划文件，不会调用模型或从问句生成SQL。

```json
{
  "workflow": "weekly_report",
  "report_date": "2026-10-17",
  "queries": [
    {"sql_file":"../../knowledge/sql_examples/period_metrics.sql","result_kind":"metrics","window":"current","label":"本期五项指标"},
    {"sql_file":"../../knowledge/sql_examples/period_comparison.sql","result_kind":"comparison","window":"comparison","label":"整体与层级变化"}
  ],
  "notes": {"observations":["根据实际工具结果填写定性观察。"]}
}
```

sql_file相对计划文件所在目录解析；也可直接写sql字符串，二者选一。额外查询可添加filters（streamer_tier/streamer_id，只能缩小计划范围），result_kind=table可返回补充聚合表。only_if_alerts=true表示仅在此前查询已有is_anomaly=1时执行；这只是重放条件分支，不是模型自主调查。

活动使用workflow=campaign_review、campaign_id替代report_date；助推用workflow=traffic_boost_update和report_date，所需查询为metrics+boost。自助问数可用workflow=ad_hoc及start_date/end_date，完整导出计划只需metrics查询；单项问数直接调用工具使用table结果即可。

日期与口径参数由工具绑定，不能覆盖。当前窗口使用current，比较查询使用comparison，返回契约见knowledge/rules.md。SQL写SQLite方言，只访问knowledge/schema.json中的逻辑数据源。query执行成功不等于业务语义已获证明；需核对示例或独立查询。

同run_id、同计划/SQL/知识版本/数据快照重放返回已完成产物；计划、知识或数据变更需新run_id。失败会留下plan_failure.json与工具证据，修复后使用新run_id。生成看板和delivery_draft.json，不会真实发送。
