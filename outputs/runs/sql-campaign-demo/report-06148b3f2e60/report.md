# 活动复盘 · 2026-10-14

100% 合成数据 · Asia/Jakarta · 内部草稿 · 未对外发送

运行：`sql-campaign-demo`；快照：`0cec2dce7448a98137559f8cb6485a47d85baa016d7ebeea7ee0824991f8dbae`；口径：`knowledge-sql-v3`。

## 活动复盘 · e0006

### 本期核心指标

| 分组 | 指标 | 数值 | 单位 |
| --- | --- | --- | --- |
| all | 打赏金额 | 38,390,000 | IDR |
| all | 看播时长 | 2,297.39 | hours |
| all | 有效直播天数 | 138 | streamer-days |
| all | 直播时长 | 349.25 | hours |
| all | 观看观众数 | 2,905 | users |

对比区间：2026-10-01 至 2026-10-07

| 指标 | 本期 | 上期 | 变化 | 监控状态 |
| --- | --- | --- | --- | --- |
| 有效直播天数 | 138 | 134 | 2.99% | 未触发 |
| 打赏金额 | 38,390,000 | 38,140,000 | 0.66% | 未触发 |
| 直播时长 | 349.25 | 349.50 | -0.07% | 未触发 |
| 观看观众数 | 2,905 | 2,780 | 4.50% | 未触发 |
| 看播时长 | 2,297.39 | 2,040.14 | 12.61% | 未触发 |

| 层级 | 指标 | 变化 | 状态 |
| --- | --- | --- | --- |
| mid | 有效直播天数 | 13.85% | 未触发 |
| mid | 打赏金额 | -2.31% | 未触发 |
| mid | 直播时长 | 12.04% | 未触发 |
| mid | 观看观众数 | 7.84% | 未触发 |
| mid | 看播时长 | 16.53% | 未触发 |
| tail | 有效直播天数 | -7.25% | 未触发 |
| tail | 打赏金额 | 3.62% | 未触发 |
| tail | 直播时长 | -11.31% | 未触发 |
| tail | 观看观众数 | 5.78% | 未触发 |
| tail | 看播时长 | 8.73% | 未触发 |

### 活动名单本期指标 · e0004

```sql
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

[查询结果与实际执行证据](e0004.json)

### 同名单活动前后对比 · e0005

```sql
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

[查询结果与实际执行证据](e0005.json)

> SQL访问与结果形状已校验，不等于自动证明业务口径正确；解释需人工审阅。

[原始工具结果与 SQL 证据](e0006.json)

查询：`q-2c4dfc4b15786e20`, `q-51fb538bd582945f`, `q-1666b3e2370c8b29`, `q-572c3bdb3257f94e`, `q-bbf96a7cceba946c`, `q-f85b0ae52027c4e3`, `q-60ccab1988d0920c`, `q-c9512f741d9c618a`, `q-daac359a5f9a203e`, `q-ee38adb2ff0ed7c6`, `q-6c1eaf0d2672e31b`, `q-02991d4632b385c9`, `q-4572ef5bcd1d3fd3`, `q-4e2c2a4af52a6e23`, `q-509379b492684985`, `q-c67fe3a82bec6a26`, `q-405a5267bc81982e`, `q-85ec192a5b4d782d`, `q-644580f650525001`, `q-d40444766662438b`, `q-f1ca314acc6ae0ea`, `q-e6eab6261a8ef93b`, `q-216ff09b1f852ddc`, `q-c59562124e68dbb9`, `q-3a40db1b68cc7009`, `q-69560a4072d373b4`, `q-020d10321fbc5210`, `q-09807395ef5f9562`, `q-feb5d505e6b8f6bd`, `q-ddd4c36339e3fd6a`, `q-30a90e41c6045322`, `q-879eb4435d2d901f`, `q-f55247d2198f4162`, `q-cf700dda5e0559f1`, `q-66ec022dc581257c`, `q-2b34df5ab392d240`, `q-901bc61922421f84`, `q-2759ef9759809bad`

## Agent 观察

- 活动期与活动前等长窗口保持同一主播名单，按共享口径比较。 [e0006]

## 待验证的解释

- 前后差异可能同时包含流量和开播供给变化，不能作为活动因果收益。 [e0006]

## 分析边界

仅合成数据与待审核草稿；活动前后变化不证明因果。有效直播门槛见统一指标配置。内部数据系统、实际流量下发与定时推送尚未接入，未实测节省工时。
