-- 最近七天主播级指标与昨日实际额度；规则仅产生待审核建议。
WITH watch_day AS (
  SELECT date, streamer_id, SUM(duration_seconds) AS watch_seconds FROM watch_events GROUP BY date, streamer_id
), watches AS (
  SELECT streamer_id, SUM(duration_seconds) / 3600.0 AS watch_duration_hours,
         COUNT(DISTINCT viewer_id) AS viewer_uv FROM watch_events GROUP BY streamer_id
), gifts AS (
  SELECT streamer_id, SUM(amount_idr) AS gift_amount_idr FROM gift_events GROUP BY streamer_id
), live AS (
  SELECT b.streamer_id, SUM(b.live_seconds) / 3600.0 AS live_duration_hours,
         SUM(CASE WHEN b.live_seconds > 0 AND b.live_seconds >= :min_live_seconds
                  AND COALESCE(w.watch_seconds, 0) >= :min_watch_seconds THEN 1 ELSE 0 END) AS effective_live_days
  FROM broadcast_days b LEFT JOIN watch_day w ON b.date = w.date AND b.streamer_id = w.streamer_id
  GROUP BY b.streamer_id
), base AS (
  SELECT s.streamer_id, s.tier AS streamer_tier,
         COALESCE(g.gift_amount_idr, 0) AS gift_amount_idr,
         COALESCE(w.watch_duration_hours, 0) AS watch_duration_hours,
         COALESCE(l.effective_live_days, 0) AS effective_live_days,
         COALESCE(l.live_duration_hours, 0) AS live_duration_hours,
         COALESCE(w.viewer_uv, 0) AS viewer_uv, b.allocated_units AS previous_units
  FROM streamer_profiles s LEFT JOIN watches w ON s.streamer_id = w.streamer_id
  LEFT JOIN gifts g ON s.streamer_id = g.streamer_id LEFT JOIN live l ON s.streamer_id = l.streamer_id
  LEFT JOIN boost_snapshots b ON s.streamer_id = b.streamer_id AND b.date = :previous_snapshot_date
), suggested AS (
  SELECT streamer_id, streamer_tier, gift_amount_idr, watch_duration_hours, effective_live_days,
         live_duration_hours, viewer_uv, previous_units,
         CASE WHEN effective_live_days >= :boost_days AND viewer_uv >= :boost_viewers THEN 1 ELSE 0 END AS eligible,
         CASE WHEN effective_live_days >= :boost_days AND viewer_uv >= :boost_viewers THEN :boost_units ELSE 0 END AS suggested_units
  FROM base
)
SELECT streamer_id, streamer_tier, gift_amount_idr, watch_duration_hours, effective_live_days,
       live_duration_hours, viewer_uv, eligible, previous_units, suggested_units,
       suggested_units - previous_units AS delta_units,
       CASE WHEN previous_units IS NULL THEN 'review_missing_snapshot'
            WHEN suggested_units > previous_units THEN 'increase'
            WHEN suggested_units < previous_units THEN 'decrease' ELSE 'keep' END AS action,
       CASE WHEN eligible = 1 THEN '达到有效开播与观众门槛' ELSE '未达到有效开播或观众门槛' END AS reason
FROM suggested ORDER BY eligible DESC, watch_duration_hours DESC, streamer_id
