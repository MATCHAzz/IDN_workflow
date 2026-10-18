# 任务与分析规则

## 周报

截至日往前7天对此前7天。先查询本期五项指标，再用SQL比较两个窗口；同时检查整体和层级结果。只有整体未告警不能称所有层级正常。

下降提醒：相对变化<=-:drop_threshold且两期观看UV均>=:min_viewers。基线为0或样本不足时is_anomaly为NULL，status分别为zero_baseline或small_sample；正常可判断为ok。阈值由工具注入，禁止参数覆盖。没有统计显著性或因果意义。

## 活动复盘

活动起止时间与冻结名单由prepare_analysis从活动配置读取。基线为活动前相同长度窗口。两期都使用同一名单；前后差异不等于AB因果效应。没有成本账时不算ROI、真实毛利。

## 主播助推

最近7天有效主播日>=:boost_days、期间观看UV>=:boost_viewers时eligible=1，建议:boost_units，否则建议0。对比:previous_snapshot_date的实际额度，输出previous_units/suggested_units/delta_units/action/reason。按eligible、看播时长排序。输出完整合成主播名单，只保存待审核CSV，不下发。该配额规则是Demo假设，不是最优流量模型。

## SQL结果契约

- metrics：dimension + 五项指标列，按整体/层级/主播聚合。
- comparison：dimension, metric, current, baseline, delta, relative_change, is_anomaly, status。metric仅取五项指标key；relative_change在零基线时为NULL。可附current_viewer_uv/baseline_viewer_uv辅助复核。
- boost：streamer_id, streamer_tier, 五项指标, eligible, previous_units, suggested_units, delta_units, action, reason。
- table：补充分析用的聚合表；需给出有意义的列名。仅标准数值列可画图，不视为已验证核心指标。

执行成功只说明SQL只读、来源与输出形状符合工具约束，不证明JOIN、业务公式和因果解释正确；Agent必须检查知识库口径，并用已验证示例或对照查询复核。
