-- 示例Agent在层级提醒后选择的补充聚合查询；按计划范围进一步筛选尾部主播。
SELECT w.streamer_id, s.tier AS streamer_tier,
       COUNT(DISTINCT w.viewer_id) AS viewer_uv,
       SUM(w.duration_seconds) / 3600.0 AS watch_duration_hours
FROM watch_events w JOIN streamer_profiles s ON w.streamer_id = s.streamer_id
GROUP BY w.streamer_id, s.tier
ORDER BY watch_duration_hours DESC, w.streamer_id
