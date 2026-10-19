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
