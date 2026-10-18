# SQL示例的使用方式

这些是可执行、经核对的参考查询，不是自动选取的模板引擎。Agent先读口径与表结构，再选取参考，按用户要求改写SQL、选择范围、执行并检查结果。

- period_metrics.sql：所选范围内整体五指标。
- period_comparison.sql：本期对基线，整体与主播层级同时比较；适用于周报/活动，实际窗口和名单由prepare_analysis固定。
- boost_candidates.sql：主播级指标与助推更新建议。

执行时逻辑源会自动限制到指定窗口和主播范围。不要替换成物理表名，不要覆盖工具参数。涉及viewer_id只能写COUNT(DISTINCT viewer_id)。多个事实表先聚合再JOIN。

新增SQL应使用独立SQL对照或金额/时长勾稽核对后再沉淀，不能因为“执行成功”就称指标正确。当前SQL方言为SQLite。
