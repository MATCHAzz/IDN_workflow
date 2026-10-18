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
