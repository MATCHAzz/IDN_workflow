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
