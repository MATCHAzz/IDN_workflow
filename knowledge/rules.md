# 任务与分析规则

## 通用约束

业务时区固定Asia/Jakarta，先确认数据范围，不将超出快照的日期静默替换。Agent只使用schema.json暴露的逻辑源，通过execute_readonly_sql执行；viewer_id仅可COUNT(DISTINCT viewer_id)，不返回用户明细。多个事实表先各自聚合再关联，期间UV不可相加每日或各主播UV。

质量失败停止分析与导出，不把缺失日志当零。阈值仅来自config/operations_metrics.json。所有步骤复用同run和计划；知识或快照改变后用新run重新查询，不混用旧证据。未知指标或缺失数据需说明，不编造。报告与助推清单是待审核草稿，不代表实际发送或流量下发。

## 周报

截至日往前7天对此前7天。先查询本期五项指标，再用SQL比较两个窗口；同时检查整体和层级结果。只有整体未告警不能称所有层级正常。

## 异常监控

下降提醒：相对变化<=-:drop_threshold且两期观看UV均>=:min_viewers。基线为0或样本不足时is_anomaly为NULL，status分别为zero_baseline或small_sample；正常可判断为ok。阈值由工具注入，禁止参数覆盖。没有统计显著性或因果意义。

## 活动复盘

活动起止时间与冻结名单由prepare_analysis从活动配置读取。基线为活动前相同长度窗口。两期都使用同一名单；前后差异不等于AB因果效应。没有成本账时不算ROI、真实毛利。

## 主播助推

最近7天有效主播日>=:boost_days、期间观看UV>=:boost_viewers时eligible=1，建议:boost_units，否则建议0。对比:previous_snapshot_date的实际额度，输出previous_units/suggested_units/delta_units/action/reason。按eligible、看播时长排序。输出完整合成主播名单，只保存待审核CSV，不下发。该配额规则是Demo假设，不是最优流量模型。

## 数据质量

get_data_profile用于确认日期、活动和快照，不代表质检通过。check_data_quality检查主键、关联、每日覆盖、支付对账及主播日志和助推快照完整性；quality_status=failed或工具error时停止下游分析与导出。具体失败项以工具证据为准。

## 下钻

先使用已有整体和层级比较结果，再按相关层级或主播补查，不固定跑满所有维度。保持原任务日期与名单，追加filters只能缩小范围。先核对有效直播天数和直播时长，再看观看时长与观众数，最后看打赏；已有证据足够则停止。事实、候选解释和验证缺口分开，不能据前后变化声称因果。

## 报告交付

assemble_analysis引用同任务的SQL证据，export_report渲染报告，prepare_delivery保存待推送包并更新工作台。notes中的定性观察引用evidence_ids，不手填业务数字。知识、配置、快照和计划须一致；草稿状态draft_not_sent不等于已发送。

## SQL结果契约

- metrics：dimension + 五项指标列，按整体/层级/主播聚合。
- comparison：dimension, metric, current, baseline, delta, relative_change, is_anomaly, status。metric仅取五项指标key；relative_change在零基线时为NULL。可附current_viewer_uv/baseline_viewer_uv辅助复核。
- boost：streamer_id, streamer_tier, 五项指标, eligible, previous_units, suggested_units, delta_units, action, reason。
- table：补充分析用的聚合表；需给出有意义的列名。仅标准数值列可画图，不视为已验证核心指标。

执行成功只说明SQL只读、来源与输出形状符合工具约束，不证明JOIN、业务公式和因果解释正确；Agent必须检查知识库口径，并用已验证示例或对照查询复核。
