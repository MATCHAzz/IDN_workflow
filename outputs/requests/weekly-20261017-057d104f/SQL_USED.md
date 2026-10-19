# 本次周报实际使用的 SQL

运行：`weekly-20261017-057d104f`。业务时区：Asia/Jakarta。

本期：2026-10-11 至 2026-10-17；基线：2026-10-04 至 2026-10-10。

本期指标与整体/层级比较采用知识库已核对的标准查询；尾部主播比较与诊断汇总为本次告警后编写的定向下钻查询。所有查询均经 execute_readonly_sql 执行。

以下同时保留提交 SQL、工具注入范围后的实际执行 SQL 和绑定参数。

## 本周整体五项核心指标 · e0004

[提交 SQL](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/current_metrics.sql>) · [实际执行 SQL](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/current_metrics.prepared.sql>) · [完整执行证据](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0004.json>)

```sql
-- 本次周报采用知识库已核对的标准口径；日期、名单与阈值由工具绑定。
-- 整体五指标参考。日期和主播范围由工具注入，不读取物理表。
WITH watch_day AS (
  SELECT date, streamer_id, SUM(duration_seconds) AS watch_seconds
  FROM watch_events GROUP BY date, streamer_id
), watch_total AS (
  SELECT SUM(duration_seconds) / 3600.0 AS watch_duration_hours,
         COUNT(DISTINCT viewer_id) AS viewer_uv FROM watch_events
), gift_total AS (
  SELECT SUM(amount_idr) AS gift_amount_idr FROM gift_events
), live_total AS (
  SELECT SUM(b.live_seconds) / 3600.0 AS live_duration_hours,
         SUM(CASE WHEN b.live_seconds > 0 AND b.live_seconds >= :min_live_seconds
                   AND COALESCE(w.watch_seconds, 0) >= :min_watch_seconds THEN 1 ELSE 0 END) AS effective_live_days
  FROM broadcast_days b LEFT JOIN watch_day w ON b.date = w.date AND b.streamer_id = w.streamer_id
)
SELECT 'all' AS dimension, COALESCE(g.gift_amount_idr, 0) AS gift_amount_idr,
       COALESCE(w.watch_duration_hours, 0) AS watch_duration_hours,
       COALESCE(l.effective_live_days, 0) AS effective_live_days,
       COALESCE(l.live_duration_hours, 0) AS live_duration_hours, w.viewer_uv
FROM live_total l CROSS JOIN watch_total w CROSS JOIN gift_total g
```

绑定参数：

```json
{
  "start_date": "2026-10-11",
  "end_date": "2026-10-17",
  "current_start": "2026-10-11",
  "current_end": "2026-10-17",
  "baseline_start": "2026-10-04",
  "baseline_end": "2026-10-10",
  "report_date": "2026-10-17",
  "previous_snapshot_date": "2026-10-16",
  "min_live_seconds": 3600,
  "min_watch_seconds": 1800,
  "drop_threshold": 0.2,
  "min_viewers": 30,
  "boost_days": 3,
  "boost_viewers": 30,
  "boost_units": 500
}
```

## 整体及主播层级的五项指标周变化 · e0005

[提交 SQL](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/weekly_comparison.sql>) · [实际执行 SQL](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/weekly_comparison.prepared.sql>) · [完整执行证据](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0005.json>)

```sql
-- 本次周报采用知识库已核对的标准口径；日期、名单与阈值由工具绑定。
-- 相同名单、等长当前/基线窗口；整体与层级同时统计，UV各自独立去重。
WITH dimensions AS (
  SELECT 'all' AS dimension UNION ALL SELECT tier AS dimension FROM streamer_profiles GROUP BY tier
), watch_day AS (
  SELECT date, streamer_id, SUM(duration_seconds) AS watch_seconds
  FROM watch_events GROUP BY date, streamer_id
), watches AS (
  SELECT CASE WHEN v.date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         d.dimension, SUM(v.duration_seconds) / 3600.0 AS watch_duration_hours,
         COUNT(DISTINCT v.viewer_id) AS viewer_uv
  FROM watch_events v JOIN streamer_profiles s ON v.streamer_id = s.streamer_id
  JOIN dimensions d ON d.dimension = 'all' OR d.dimension = s.tier
  GROUP BY period, d.dimension
), gifts AS (
  SELECT CASE WHEN g.date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         d.dimension, SUM(g.amount_idr) AS gift_amount_idr
  FROM gift_events g JOIN streamer_profiles s ON g.streamer_id = s.streamer_id
  JOIN dimensions d ON d.dimension = 'all' OR d.dimension = s.tier GROUP BY period, d.dimension
), live AS (
  SELECT CASE WHEN b.date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         d.dimension, SUM(b.live_seconds) / 3600.0 AS live_duration_hours,
         SUM(CASE WHEN b.live_seconds > 0 AND b.live_seconds >= :min_live_seconds
                   AND COALESCE(w.watch_seconds, 0) >= :min_watch_seconds THEN 1 ELSE 0 END) AS effective_live_days
  FROM broadcast_days b JOIN streamer_profiles s ON b.streamer_id = s.streamer_id
  JOIN dimensions d ON d.dimension = 'all' OR d.dimension = s.tier
  LEFT JOIN watch_day w ON b.date = w.date AND b.streamer_id = w.streamer_id
  GROUP BY period, d.dimension
), wide AS (
  SELECT l.period, l.dimension, COALESCE(g.gift_amount_idr, 0) AS gift_amount_idr,
         COALESCE(w.watch_duration_hours, 0) AS watch_duration_hours,
         l.effective_live_days, l.live_duration_hours, COALESCE(w.viewer_uv, 0) AS viewer_uv
  FROM live l LEFT JOIN watches w ON l.period = w.period AND l.dimension = w.dimension
  LEFT JOIN gifts g ON l.period = g.period AND l.dimension = g.dimension
), metric_values AS (
  SELECT period, dimension, 'gift_amount_idr' AS metric, gift_amount_idr AS value, viewer_uv FROM wide
  UNION ALL SELECT period, dimension, 'watch_duration_hours', watch_duration_hours, viewer_uv FROM wide
  UNION ALL SELECT period, dimension, 'effective_live_days', effective_live_days, viewer_uv FROM wide
  UNION ALL SELECT period, dimension, 'live_duration_hours', live_duration_hours, viewer_uv FROM wide
  UNION ALL SELECT period, dimension, 'viewer_uv', viewer_uv, viewer_uv FROM wide
), pivoted AS (
  SELECT dimension, metric,
         MAX(CASE WHEN period = 'current' THEN value END) AS current,
         MAX(CASE WHEN period = 'baseline' THEN value END) AS baseline,
         MAX(CASE WHEN period = 'current' THEN viewer_uv END) AS current_viewer_uv,
         MAX(CASE WHEN period = 'baseline' THEN viewer_uv END) AS baseline_viewer_uv
  FROM metric_values GROUP BY dimension, metric
), changes AS (
  SELECT dimension, metric, current, baseline, current_viewer_uv, baseline_viewer_uv,
         current - baseline AS delta,
         CASE WHEN baseline = 0 THEN NULL ELSE (current - baseline) * 1.0 / baseline END AS relative_change
  FROM pivoted
)
SELECT dimension, metric, current, baseline, delta, relative_change, current_viewer_uv, baseline_viewer_uv,
       CASE WHEN baseline = 0 OR current_viewer_uv < :min_viewers OR baseline_viewer_uv < :min_viewers THEN NULL
            WHEN relative_change <= -:drop_threshold THEN 1 ELSE 0 END AS is_anomaly,
       CASE WHEN baseline = 0 THEN 'zero_baseline'
            WHEN current_viewer_uv < :min_viewers OR baseline_viewer_uv < :min_viewers THEN 'small_sample'
            ELSE 'ok' END AS status
FROM changes ORDER BY dimension, metric
```

绑定参数：

```json
{
  "start_date": "2026-10-04",
  "end_date": "2026-10-17",
  "current_start": "2026-10-11",
  "current_end": "2026-10-17",
  "baseline_start": "2026-10-04",
  "baseline_end": "2026-10-10",
  "report_date": "2026-10-17",
  "previous_snapshot_date": "2026-10-16",
  "min_live_seconds": 3600,
  "min_watch_seconds": 1800,
  "drop_threshold": 0.2,
  "min_viewers": 30,
  "boost_days": 3,
  "boost_viewers": 30,
  "boost_units": 500
}
```

## 尾部主播同名单前后五指标下钻，按看播时长差值排序 · e0006

[提交 SQL](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_streamer_comparison.sql>) · [实际执行 SQL](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_streamer_comparison.prepared.sql>) · [完整执行证据](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0006.json>)

```sql
-- 尾部层级告警后的定向下钻。范围由同一任务计划进一步收窄到 tail。
-- 各明细事实先按主播/周期聚合，单主播期间 UV 独立去重，不能相加为层级 UV。
WITH periods AS (
  SELECT 'current' AS period UNION ALL SELECT 'baseline'
), watch_day AS (
  SELECT date, streamer_id, SUM(duration_seconds) AS watch_seconds
  FROM watch_events
  GROUP BY date, streamer_id
), watching AS (
  SELECT streamer_id,
         CASE WHEN date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         SUM(duration_seconds) / 3600.0 AS watch_duration_hours,
         COUNT(DISTINCT viewer_id) AS viewer_uv
  FROM watch_events
  GROUP BY streamer_id, period
), gifting AS (
  SELECT streamer_id,
         CASE WHEN date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         SUM(amount_idr) AS gift_amount_idr
  FROM gift_events
  GROUP BY streamer_id, period
), broadcasting AS (
  SELECT b.streamer_id,
         CASE WHEN b.date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         SUM(b.live_seconds) / 3600.0 AS live_duration_hours,
         SUM(CASE WHEN b.live_seconds > 0 AND b.live_seconds >= :min_live_seconds
                        AND COALESCE(w.watch_seconds, 0) >= :min_watch_seconds THEN 1 ELSE 0 END) AS effective_live_days
  FROM broadcast_days b
  LEFT JOIN watch_day w ON b.date = w.date AND b.streamer_id = w.streamer_id
  GROUP BY b.streamer_id, period
), per_period AS (
  SELECT s.streamer_id, s.tier AS streamer_tier, p.period,
         COALESCE(w.watch_duration_hours, 0) AS watch_duration_hours,
         COALESCE(w.viewer_uv, 0) AS viewer_uv,
         COALESCE(g.gift_amount_idr, 0) AS gift_amount_idr,
         COALESCE(b.live_duration_hours, 0) AS live_duration_hours,
         COALESCE(b.effective_live_days, 0) AS effective_live_days
  FROM streamer_profiles s CROSS JOIN periods p
  LEFT JOIN watching w ON s.streamer_id = w.streamer_id AND p.period = w.period
  LEFT JOIN gifting g ON s.streamer_id = g.streamer_id AND p.period = g.period
  LEFT JOIN broadcasting b ON s.streamer_id = b.streamer_id AND p.period = b.period
), paired AS (
  SELECT c.streamer_id, c.streamer_tier,
         c.effective_live_days AS current_effective_live_days, b.effective_live_days AS baseline_effective_live_days,
         c.live_duration_hours AS current_live_duration_hours, b.live_duration_hours AS baseline_live_duration_hours,
         c.watch_duration_hours AS current_watch_duration_hours, b.watch_duration_hours AS baseline_watch_duration_hours,
         c.viewer_uv AS current_viewer_uv, b.viewer_uv AS baseline_viewer_uv,
         c.gift_amount_idr AS current_gift_amount_idr, b.gift_amount_idr AS baseline_gift_amount_idr
  FROM per_period c JOIN per_period b ON c.streamer_id = b.streamer_id
  WHERE c.period = 'current' AND b.period = 'baseline'
)
SELECT streamer_id, streamer_tier,
       current_effective_live_days, baseline_effective_live_days,
       current_effective_live_days - baseline_effective_live_days AS effective_live_days_delta,
       current_live_duration_hours, baseline_live_duration_hours,
       current_live_duration_hours - baseline_live_duration_hours AS live_duration_hours_delta,
       current_watch_duration_hours, baseline_watch_duration_hours,
       current_watch_duration_hours - baseline_watch_duration_hours AS watch_duration_hours_delta,
       CASE WHEN baseline_watch_duration_hours = 0 THEN NULL
            ELSE (current_watch_duration_hours - baseline_watch_duration_hours) / baseline_watch_duration_hours END AS watch_relative_change,
       current_viewer_uv, baseline_viewer_uv,
       current_viewer_uv - baseline_viewer_uv AS viewer_uv_delta,
       CASE WHEN baseline_viewer_uv = 0 THEN NULL
            ELSE (current_viewer_uv - baseline_viewer_uv) * 1.0 / baseline_viewer_uv END AS viewer_relative_change,
       current_gift_amount_idr, baseline_gift_amount_idr,
       current_gift_amount_idr - baseline_gift_amount_idr AS gift_amount_idr_delta,
       CASE WHEN baseline_watch_duration_hours = 0 THEN 'zero_baseline'
            WHEN current_viewer_uv < :min_viewers OR baseline_viewer_uv < :min_viewers THEN 'small_sample'
            ELSE 'ok' END AS watch_status,
       CASE WHEN baseline_watch_duration_hours = 0 OR current_viewer_uv < :min_viewers OR baseline_viewer_uv < :min_viewers THEN NULL
            WHEN (current_watch_duration_hours - baseline_watch_duration_hours) / baseline_watch_duration_hours <= -:drop_threshold THEN 1 ELSE 0 END AS is_anomaly
FROM paired
ORDER BY watch_duration_hours_delta, streamer_id
```

绑定参数：

```json
{
  "start_date": "2026-10-04",
  "end_date": "2026-10-17",
  "current_start": "2026-10-11",
  "current_end": "2026-10-17",
  "baseline_start": "2026-10-04",
  "baseline_end": "2026-10-10",
  "report_date": "2026-10-17",
  "previous_snapshot_date": "2026-10-16",
  "min_live_seconds": 3600,
  "min_watch_seconds": 1800,
  "drop_threshold": 0.2,
  "min_viewers": 30,
  "boost_days": 3,
  "boost_viewers": 30,
  "boost_units": 500,
  "scope_tier": "tail"
}
```

## 尾部观看下降覆盖范围、开播变化与损失集中度；仅汇总可加指标 · e0008

[提交 SQL](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_diagnostic_summary.sql>) · [实际执行 SQL](</Users/matchalee/Desktop/IDN Workflow/outputs/requests/weekly-20261017-057d104f/tail_diagnostic_summary.prepared.sql>) · [完整执行证据](</Users/matchalee/Desktop/IDN Workflow/outputs/runs/weekly-20261017-057d104f/e0008.json>)

```sql
-- 尾部层级告警后的定向下钻。范围由同一任务计划进一步收窄到 tail。
-- 各明细事实先按主播/周期聚合，单主播期间 UV 独立去重，不能相加为层级 UV。
WITH periods AS (
  SELECT 'current' AS period UNION ALL SELECT 'baseline'
), watch_day AS (
  SELECT date, streamer_id, SUM(duration_seconds) AS watch_seconds
  FROM watch_events
  GROUP BY date, streamer_id
), watching AS (
  SELECT streamer_id,
         CASE WHEN date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         SUM(duration_seconds) / 3600.0 AS watch_duration_hours,
         COUNT(DISTINCT viewer_id) AS viewer_uv
  FROM watch_events
  GROUP BY streamer_id, period
), gifting AS (
  SELECT streamer_id,
         CASE WHEN date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         SUM(amount_idr) AS gift_amount_idr
  FROM gift_events
  GROUP BY streamer_id, period
), broadcasting AS (
  SELECT b.streamer_id,
         CASE WHEN b.date BETWEEN :current_start AND :current_end THEN 'current' ELSE 'baseline' END AS period,
         SUM(b.live_seconds) / 3600.0 AS live_duration_hours,
         SUM(CASE WHEN b.live_seconds > 0 AND b.live_seconds >= :min_live_seconds
                        AND COALESCE(w.watch_seconds, 0) >= :min_watch_seconds THEN 1 ELSE 0 END) AS effective_live_days
  FROM broadcast_days b
  LEFT JOIN watch_day w ON b.date = w.date AND b.streamer_id = w.streamer_id
  GROUP BY b.streamer_id, period
), per_period AS (
  SELECT s.streamer_id, s.tier AS streamer_tier, p.period,
         COALESCE(w.watch_duration_hours, 0) AS watch_duration_hours,
         COALESCE(w.viewer_uv, 0) AS viewer_uv,
         COALESCE(g.gift_amount_idr, 0) AS gift_amount_idr,
         COALESCE(b.live_duration_hours, 0) AS live_duration_hours,
         COALESCE(b.effective_live_days, 0) AS effective_live_days
  FROM streamer_profiles s CROSS JOIN periods p
  LEFT JOIN watching w ON s.streamer_id = w.streamer_id AND p.period = w.period
  LEFT JOIN gifting g ON s.streamer_id = g.streamer_id AND p.period = g.period
  LEFT JOIN broadcasting b ON s.streamer_id = b.streamer_id AND p.period = b.period
), paired AS (
  SELECT c.streamer_id, c.streamer_tier,
         c.effective_live_days AS current_effective_live_days, b.effective_live_days AS baseline_effective_live_days,
         c.live_duration_hours AS current_live_duration_hours, b.live_duration_hours AS baseline_live_duration_hours,
         c.watch_duration_hours AS current_watch_duration_hours, b.watch_duration_hours AS baseline_watch_duration_hours,
         c.viewer_uv AS current_viewer_uv, b.viewer_uv AS baseline_viewer_uv,
         c.gift_amount_idr AS current_gift_amount_idr, b.gift_amount_idr AS baseline_gift_amount_idr
  FROM per_period c JOIN per_period b ON c.streamer_id = b.streamer_id
  WHERE c.period = 'current' AND b.period = 'baseline'
), deltas AS (
  SELECT streamer_id, current_watch_duration_hours, baseline_watch_duration_hours, current_viewer_uv, baseline_viewer_uv, current_live_duration_hours, baseline_live_duration_hours, current_effective_live_days, baseline_effective_live_days, current_gift_amount_idr, baseline_gift_amount_idr, current_watch_duration_hours - baseline_watch_duration_hours AS watch_delta,
         CASE WHEN current_watch_duration_hours < baseline_watch_duration_hours
              THEN baseline_watch_duration_hours - current_watch_duration_hours ELSE 0 END AS lost_watch_hours
  FROM paired
), totals AS (
  SELECT COUNT(*) AS total_streamers,
         SUM(CASE WHEN watch_delta < 0 THEN 1 ELSE 0 END) AS watch_declining_streamers,
         SUM(CASE WHEN current_viewer_uv < baseline_viewer_uv THEN 1 ELSE 0 END) AS viewer_declining_streamers,
         SUM(CASE WHEN watch_delta < 0 AND current_live_duration_hours >= baseline_live_duration_hours THEN 1 ELSE 0 END) AS watch_decline_without_live_decline_streamers,
         SUM(CASE WHEN baseline_watch_duration_hours = 0 OR current_viewer_uv < :min_viewers OR baseline_viewer_uv < :min_viewers THEN 1 ELSE 0 END) AS watch_indeterminate_streamers,
         SUM(CASE WHEN baseline_watch_duration_hours > 0 AND current_viewer_uv >= :min_viewers AND baseline_viewer_uv >= :min_viewers
                       AND watch_delta / baseline_watch_duration_hours <= -:drop_threshold THEN 1 ELSE 0 END) AS watch_alert_streamers,
         SUM(current_effective_live_days) AS current_effective_live_days,
         SUM(baseline_effective_live_days) AS baseline_effective_live_days,
         SUM(current_live_duration_hours) AS current_live_duration_hours,
         SUM(baseline_live_duration_hours) AS baseline_live_duration_hours,
         SUM(current_watch_duration_hours) AS current_watch_duration_hours,
         SUM(baseline_watch_duration_hours) AS baseline_watch_duration_hours,
         SUM(current_gift_amount_idr) AS current_gift_amount_idr,
         SUM(baseline_gift_amount_idr) AS baseline_gift_amount_idr,
         SUM(lost_watch_hours) AS gross_lost_watch_hours
  FROM deltas
), largest_losses AS (
  SELECT streamer_id, lost_watch_hours
  FROM deltas WHERE lost_watch_hours > 0
  ORDER BY lost_watch_hours DESC, streamer_id LIMIT 3
), top_losses AS (
  SELECT SUM(lost_watch_hours) AS top_three_lost_watch_hours FROM largest_losses
)
SELECT t.total_streamers, t.watch_declining_streamers, t.viewer_declining_streamers, t.watch_decline_without_live_decline_streamers, t.watch_indeterminate_streamers, t.watch_alert_streamers, t.current_effective_live_days, t.baseline_effective_live_days, t.current_live_duration_hours, t.baseline_live_duration_hours, t.current_watch_duration_hours, t.baseline_watch_duration_hours, t.current_gift_amount_idr, t.baseline_gift_amount_idr, t.gross_lost_watch_hours, l.top_three_lost_watch_hours,
       CASE WHEN t.gross_lost_watch_hours = 0 THEN NULL
            ELSE l.top_three_lost_watch_hours / t.gross_lost_watch_hours END AS top_three_share_of_gross_watch_loss,
       t.current_effective_live_days - t.baseline_effective_live_days AS effective_live_days_delta,
       t.current_live_duration_hours - t.baseline_live_duration_hours AS live_duration_hours_delta,
       t.current_watch_duration_hours - t.baseline_watch_duration_hours AS watch_duration_hours_delta,
       t.current_gift_amount_idr - t.baseline_gift_amount_idr AS gift_amount_idr_delta
FROM totals t CROSS JOIN top_losses l
```

绑定参数：

```json
{
  "start_date": "2026-10-04",
  "end_date": "2026-10-17",
  "current_start": "2026-10-11",
  "current_end": "2026-10-17",
  "baseline_start": "2026-10-04",
  "baseline_end": "2026-10-10",
  "report_date": "2026-10-17",
  "previous_snapshot_date": "2026-10-16",
  "min_live_seconds": 3600,
  "min_watch_seconds": 1800,
  "drop_threshold": 0.2,
  "min_viewers": 30,
  "boost_days": 3,
  "boost_viewers": 30,
  "boost_units": 500,
  "scope_tier": "tail"
}
```

## 核对与限制

- 本期五指标与比较查询的整体本期值一致。
- 尾部主播汇总的可加指标与层级比较一致；观看 UV 始终在各自范围独立去重。
- 质量门禁、任务范围和知识版本均通过核对。
- 失败的通配符查询保留为 e0007，未作为报告证据；修正后执行成功的版本为 e0008。
- 本次为合成数据分析，聚合差异不证明因果，待推送草稿未发送。
