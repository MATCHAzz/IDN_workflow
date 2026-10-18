# 主播流量助推更新 · 2026-10-17

100% 合成数据 · Asia/Jakarta · 内部草稿 · 未对外发送

运行：`sql-boost-demo`；快照：`0cec2dce7448a98137559f8cb6485a47d85baa016d7ebeea7ee0824991f8dbae`；口径：`knowledge-sql-v3`。

## 主播流量助推更新 · e0006

### 本期核心指标

| 分组 | 指标 | 数值 | 单位 |
| --- | --- | --- | --- |
| all | 打赏金额 | 51,230,000 | IDR |
| all | 看播时长 | 2,889.96 | hours |
| all | 有效直播天数 | 203 | streamer-days |
| all | 直播时长 | 501.50 | hours |
| all | 观看观众数 | 3,137 | users |

助推清单见同目录 traffic_boost_candidates.csv；仅为待审核草稿。

| 主播 | 层级 | 有效天数 | 观看UV | 原额度 | 建议额度 | 操作 |
| --- | --- | --- | --- | --- | --- | --- |
| 32 | mid | 6 | 183 | 0 | 500 | increase |
| 29 | mid | 6 | 154 | 500 | 500 | keep |
| 47 | mid | 4 | 196 | 0 | 500 | increase |
| 20 | mid | 6 | 145 | 0 | 500 | increase |
| 41 | mid | 4 | 179 | 200 | 500 | increase |
| 23 | mid | 5 | 138 | 200 | 500 | increase |
| 59 | mid | 4 | 135 | 500 | 500 | keep |
| 56 | mid | 4 | 137 | 0 | 500 | increase |
| 34 | head | 5 | 149 | 200 | 500 | increase |
| 60 | tail | 5 | 133 | 200 | 500 | increase |
| 50 | mid | 4 | 136 | 0 | 500 | increase |
| 26 | mid | 4 | 137 | 1,000 | 500 | decrease |
| 9 | tail | 6 | 145 | 0 | 500 | increase |
| 1 | head | 5 | 119 | 500 | 500 | keep |
| 52 | head | 4 | 125 | 0 | 500 | increase |
| 38 | mid | 3 | 129 | 200 | 500 | increase |
| 42 | tail | 4 | 133 | 500 | 500 | keep |
| 15 | tail | 5 | 124 | 0 | 500 | increase |
| 10 | head | 4 | 131 | 1,000 | 500 | decrease |
| 17 | mid | 4 | 105 | 200 | 500 | increase |
| 33 | tail | 6 | 111 | 0 | 500 | increase |
| 16 | head | 4 | 129 | 200 | 500 | increase |
| 51 | tail | 5 | 122 | 0 | 500 | increase |
| 14 | mid | 3 | 100 | 0 | 500 | increase |
| 46 | head | 3 | 115 | 0 | 500 | increase |
| 19 | head | 3 | 105 | 1,000 | 500 | decrease |
| 13 | head | 4 | 100 | 0 | 500 | increase |
| 25 | head | 4 | 103 | 0 | 500 | increase |
| 22 | head | 5 | 84 | 0 | 500 | increase |
| 49 | head | 3 | 106 | 500 | 500 | keep |
| 8 | mid | 3 | 93 | 200 | 500 | increase |
| 12 | tail | 3 | 87 | 200 | 500 | increase |
| 40 | head | 3 | 112 | 0 | 500 | increase |
| 45 | tail | 4 | 108 | 1,000 | 500 | decrease |
| 31 | head | 3 | 79 | 500 | 500 | keep |
| 3 | tail | 3 | 97 | 0 | 500 | increase |
| 28 | head | 3 | 78 | 0 | 500 | increase |
| 58 | head | 3 | 72 | 1,000 | 500 | decrease |
| 27 | tail | 4 | 59 | 500 | 500 | keep |
| 18 | tail | 3 | 76 | 0 | 500 | increase |
| 57 | tail | 3 | 72 | 500 | 500 | keep |
| 48 | tail | 4 | 42 | 200 | 500 | increase |
| 24 | tail | 3 | 47 | 200 | 500 | increase |
| 35 | mid | 2 | 172 | 0 | 0 | keep |
| 2 | mid | 2 | 176 | 500 | 0 | decrease |
| 11 | mid | 1 | 123 | 200 | 0 | decrease |
| 5 | mid | 2 | 133 | 500 | 0 | decrease |
| 4 | head | 2 | 107 | 0 | 0 | keep |
| 53 | mid | 2 | 81 | 0 | 0 | keep |
| 6 | tail | 2 | 82 | 0 | 0 | keep |
| 37 | head | 2 | 80 | 0 | 0 | keep |
| 7 | head | 2 | 76 | 0 | 0 | keep |
| 36 | tail | 2 | 64 | 0 | 0 | keep |
| 55 | head | 0 | 99 | 0 | 0 | keep |
| 21 | tail | 1 | 79 | 0 | 0 | keep |
| 44 | mid | 1 | 80 | 200 | 0 | decrease |
| 54 | tail | 2 | 56 | 0 | 0 | keep |
| 39 | tail | 2 | 43 | 0 | 0 | keep |
| 43 | head | 2 | 54 | 0 | 0 | keep |
| 30 | tail | 2 | 26 | 0 | 0 | keep |

### 近七天运营指标 · e0004

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

### 助推更新待审核清单 · e0005

```sql
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

```

[查询结果与实际执行证据](e0005.json)

> SQL访问与结果形状已校验，不等于自动证明业务口径正确；解释需人工审阅。

[原始工具结果与 SQL 证据](e0006.json)

查询：`q-2c4dfc4b15786e20`, `q-51fb538bd582945f`, `q-1666b3e2370c8b29`, `q-572c3bdb3257f94e`, `q-bbf96a7cceba946c`, `q-f85b0ae52027c4e3`, `q-60ccab1988d0920c`, `q-c9512f741d9c618a`, `q-daac359a5f9a203e`, `q-ee38adb2ff0ed7c6`, `q-6c1eaf0d2672e31b`, `q-02991d4632b385c9`, `q-2b675bc19a4ca0a5`, `q-4e2c2a4af52a6e23`, `q-509379b492684985`, `q-c3f6b9ed67579bc8`, `q-405a5267bc81982e`, `q-85ec192a5b4d782d`, `q-a0ed556dc8b05060`, `q-d40444766662438b`, `q-f1ca314acc6ae0ea`, `q-e6eab6261a8ef93b`, `q-216ff09b1f852ddc`, `q-c59562124e68dbb9`, `q-3a40db1b68cc7009`, `q-69560a4072d373b4`, `q-020d10321fbc5210`, `q-09807395ef5f9562`, `q-feb5d505e6b8f6bd`, `q-ddd4c36339e3fd6a`, `q-30a90e41c6045322`, `q-879eb4435d2d901f`, `q-f55247d2198f4162`, `q-cf700dda5e0559f1`, `q-66ec022dc581257c`, `q-2b34df5ab392d240`, `q-901bc61922421f84`, `q-2759ef9759809bad`

## Agent 观察

- 根据统一有效开播与观众门槛生成建议，并保留与昨日额度的差值。 [e0006]

## 下一步调查

- 审核建议名单与额度后再考虑真实下发；当前只输出本地清单。 [e0006]

## 分析边界

仅合成数据与待审核草稿；活动前后变化不证明因果。有效直播门槛见统一指标配置。内部数据系统、实际流量下发与定时推送尚未接入，未实测节省工时。
