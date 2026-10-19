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
