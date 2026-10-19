WITH streamer_profiles AS (
  SELECT
    streamer_id,
    tier,
    category
  FROM streamers
), watch_events AS (
  SELECT
    date,
    user_id AS viewer_id,
    streamer_id,
    duration_seconds
  FROM view_sessions
  WHERE
    date BETWEEN :start_date AND :end_date
    AND streamer_id IN (
      SELECT
        streamer_id
      FROM streamer_profiles
    )
), gift_events AS (
  SELECT
    date,
    streamer_id,
    amount_idr
  FROM transactions
  WHERE
    date BETWEEN :start_date AND :end_date
    AND streamer_id IN (
      SELECT
        streamer_id
      FROM streamer_profiles
    )
), broadcast_days AS (
  SELECT
    date,
    streamer_id,
    live_seconds
  FROM streamer_daily
  WHERE
    date BETWEEN :start_date AND :end_date
    AND streamer_id IN (
      SELECT
        streamer_id
      FROM streamer_profiles
    )
), boost_snapshots AS (
  SELECT
    date,
    streamer_id,
    allocated_units
  FROM traffic_boost_daily
  WHERE
    date BETWEEN :start_date AND :end_date
    AND streamer_id IN (
      SELECT
        streamer_id
      FROM streamer_profiles
    )
), campaign_members AS (
  SELECT
    campaign_id,
    streamer_id
  FROM campaign_streamers
  WHERE
    streamer_id IN (
      SELECT
        streamer_id
      FROM streamer_profiles
    )
), watch_day AS (
  SELECT
    date,
    streamer_id,
    SUM(duration_seconds) AS watch_seconds
  FROM watch_events
  GROUP BY
    date,
    streamer_id
), watch_total AS (
  SELECT
    SUM(duration_seconds) / 3600.0 AS watch_duration_hours,
    COUNT(DISTINCT viewer_id) AS viewer_uv
  FROM watch_events
), gift_total AS (
  SELECT
    SUM(amount_idr) AS gift_amount_idr
  FROM gift_events
), live_total AS (
  SELECT
    SUM(b.live_seconds) / 3600.0 AS live_duration_hours,
    SUM(
      CASE
        WHEN b.live_seconds > 0
        AND b.live_seconds >= :min_live_seconds
        AND COALESCE(w.watch_seconds, 0) >= :min_watch_seconds
        THEN 1
        ELSE 0
      END
    ) AS effective_live_days
  FROM broadcast_days AS b
  LEFT JOIN watch_day AS w
    ON b.date = w.date AND b.streamer_id = w.streamer_id
)
SELECT
  'all' AS dimension,
  COALESCE(g.gift_amount_idr, 0) AS gift_amount_idr,
  COALESCE(w.watch_duration_hours, 0) AS watch_duration_hours,
  COALESCE(l.effective_live_days, 0) AS effective_live_days,
  COALESCE(l.live_duration_hours, 0) AS live_duration_hours,
  w.viewer_uv
FROM live_total AS l
CROSS JOIN watch_total AS w
CROSS JOIN gift_total AS g;
