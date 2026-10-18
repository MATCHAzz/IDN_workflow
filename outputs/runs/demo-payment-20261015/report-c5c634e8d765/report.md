# 印尼直播分析 · 2026-10-15

100% 合成数据 · Asia/Jakarta · 内部草稿 · 未对外发送

运行：`demo-payment-20261015`；快照：`1093b21f6545f248b90bedf95de6511831563cc087adaf443099115d9c21ea82`；口径：`liveops-v1`。

## check_data_quality · e0003

质量门禁：passed；29/29 项通过。

[原始工具结果与 SQL 证据](e0003.json)

查询：`q-2c4dfc4b15786e20`, `q-51fb538bd582945f`, `q-1666b3e2370c8b29`, `q-572c3bdb3257f94e`, `q-bbf96a7cceba946c`, `q-f85b0ae52027c4e3`, `q-60ccab1988d0920c`, `q-c9512f741d9c618a`, `q-daac359a5f9a203e`, `q-ee38adb2ff0ed7c6`, `q-6c1eaf0d2672e31b`, `q-02991d4632b385c9`, `q-66e7710c5045fc6f`, `q-4e2c2a4af52a6e23`, `q-509379b492684985`, `q-6392ed79b2340321`, `q-405a5267bc81982e`, `q-85ec192a5b4d782d`, `q-e5882d13e7f72e0a`, `q-d40444766662438b`, `q-f1ca314acc6ae0ea`, `q-e6eab6261a8ef93b`, `q-216ff09b1f852ddc`, `q-c59562124e68dbb9`, `q-3a40db1b68cc7009`, `q-69560a4072d373b4`, `q-020d10321fbc5210`, `q-09807395ef5f9562`, `q-feb5d505e6b8f6bd`, `q-ddd4c36339e3fd6a`

## query_kpis · e0004

| 日期 | 分组 | 指标 | 值 | 单位 |
| --- | --- | --- | --- | --- |
| 2026-10-15 | all | active_uv | 1,750 | users |
| 2026-10-15 | all | paying_uv | 134 | users |
| 2026-10-15 | all | payer_conversion | 7.66% | ratio |
| 2026-10-15 | all | payment_success_rate | 47.22% | ratio |
| 2026-10-15 | all | gross_gmv_idr | 8,900,000 | IDR |

[原始工具结果与 SQL 证据](e0004.json)

查询：`q-2c4dfc4b15786e20`, `q-51fb538bd582945f`, `q-1666b3e2370c8b29`, `q-572c3bdb3257f94e`, `q-bbf96a7cceba946c`, `q-f85b0ae52027c4e3`, `q-60ccab1988d0920c`, `q-c9512f741d9c618a`, `q-daac359a5f9a203e`, `q-ee38adb2ff0ed7c6`, `q-6c1eaf0d2672e31b`, `q-02991d4632b385c9`, `q-011c5de7535c214e`, `q-4e2c2a4af52a6e23`, `q-509379b492684985`, `q-d2316056a7c0d7b6`, `q-405a5267bc81982e`, `q-85ec192a5b4d782d`, `q-3c7693f2a3beda9d`, `q-d40444766662438b`, `q-f1ca314acc6ae0ea`, `q-e6eab6261a8ef93b`, `q-216ff09b1f852ddc`, `q-c59562124e68dbb9`, `q-3a40db1b68cc7009`, `q-69560a4072d373b4`, `q-020d10321fbc5210`, `q-09807395ef5f9562`, `q-feb5d505e6b8f6bd`, `q-ddd4c36339e3fd6a`, `q-84f7f7e6b02d447d`

## detect_anomalies · e0005

| 分组 | 指标 | 当日 | 前7日中位数 | 变化(pp / 相对%) | 告警 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| all | active_uv | 1,750 | 1,356 | 29.06% | False | ok |
| all | payer_conversion | 7.66% | 11.54% | -3.88 pp | True | ok |
| all | payment_success_rate | 47.22% | 94.24% | -47.01 pp | True | ok |
| all | gross_gmv_idr | 8,900,000 | 12,330,000 | -27.82% | False | ok |

[原始工具结果与 SQL 证据](e0005.json)

查询：`q-2c4dfc4b15786e20`, `q-51fb538bd582945f`, `q-1666b3e2370c8b29`, `q-572c3bdb3257f94e`, `q-bbf96a7cceba946c`, `q-f85b0ae52027c4e3`, `q-60ccab1988d0920c`, `q-c9512f741d9c618a`, `q-daac359a5f9a203e`, `q-ee38adb2ff0ed7c6`, `q-6c1eaf0d2672e31b`, `q-02991d4632b385c9`, `q-66e7710c5045fc6f`, `q-4e2c2a4af52a6e23`, `q-509379b492684985`, `q-6392ed79b2340321`, `q-405a5267bc81982e`, `q-85ec192a5b4d782d`, `q-e5882d13e7f72e0a`, `q-d40444766662438b`, `q-f1ca314acc6ae0ea`, `q-e6eab6261a8ef93b`, `q-216ff09b1f852ddc`, `q-c59562124e68dbb9`, `q-3a40db1b68cc7009`, `q-69560a4072d373b4`, `q-020d10321fbc5210`, `q-09807395ef5f9562`, `q-feb5d505e6b8f6bd`, `q-ddd4c36339e3fd6a`, `q-f3c4aef9579f1f88`

## get_dimension_breakdown · e0006

| 分组 | 指标 | 当日 | 前7日中位数 | 变化(pp / 相对%) | 告警 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| Android | payment_success_rate | 33.33% | 93.88% | -60.55 pp | True | ok |
| iOS | payment_success_rate | 92.16% | 94.38% | -2.23 pp | False | ok |

贡献基线使用前七天合并成功率，与告警的每日中位数不同。各组端内效应与占比效应之和等于整体变化。

整体变化：-47.60 pp。

| 分组 | 当日成功率 | 历史合并成功率 | 组内成功率效应 | 占比效应 |
| --- | --- | --- | --- | --- |
| Android | 33.33% | 94.80% | -46.96 pp | -1.31 pp |
| iOS | 92.16% | 94.89% | -0.64 pp | +1.31 pp |

[原始工具结果与 SQL 证据](e0006.json)

查询：`q-2c4dfc4b15786e20`, `q-51fb538bd582945f`, `q-1666b3e2370c8b29`, `q-572c3bdb3257f94e`, `q-bbf96a7cceba946c`, `q-f85b0ae52027c4e3`, `q-60ccab1988d0920c`, `q-c9512f741d9c618a`, `q-daac359a5f9a203e`, `q-ee38adb2ff0ed7c6`, `q-6c1eaf0d2672e31b`, `q-02991d4632b385c9`, `q-66e7710c5045fc6f`, `q-4e2c2a4af52a6e23`, `q-509379b492684985`, `q-6392ed79b2340321`, `q-405a5267bc81982e`, `q-85ec192a5b4d782d`, `q-e5882d13e7f72e0a`, `q-d40444766662438b`, `q-f1ca314acc6ae0ea`, `q-e6eab6261a8ef93b`, `q-216ff09b1f852ddc`, `q-c59562124e68dbb9`, `q-3a40db1b68cc7009`, `q-69560a4072d373b4`, `q-020d10321fbc5210`, `q-09807395ef5f9562`, `q-feb5d505e6b8f6bd`, `q-ddd4c36339e3fd6a`, `q-f97872cc476b6362`

## Agent 观察

- 质量门禁通过；当前检查未发现重复、孤儿记录或支付交易对账不一致。 [e0003]
- 观看用户增长的同时，付费转化与支付成功率均触发下降告警；支付环节值得优先排查。 [e0004, e0005]
- Android 支付成功率显著下降，iOS 未触发同样的下降阈值；端别贡献拆解表明，Android 组内成功率变化是主要负向项。 [e0006]
- GMV 也下降，但没有触发当前相对变化阈值；未告警不等于没有业务影响。 [e0005]

## 待验证的解释

- 与 Android 关联的支付链路、应用版本或支付方式差异值得核查；这些是候选解释，现有聚合数据不足以证明故障或收入变化的因果。 [e0006]

## 下一步调查

- 优先调取 Android 支付失败错误码、应用版本、网关返回码和支付方式分布，并对照 iOS 与历史同期；当前快照不含这些证据。 [e0006]
- 本轮端别拆解已足以提出调查方向，停止进一步扩展维度；如补充渠道或版本证据，再做针对性交叉验证。 [e0006]

## 分析边界

数据仅支持描述性比较和异常线索，不能证明技术故障或业务因果；缺少支付网关日志、错误码、版本与退款数据。风险规则命中仅表示待人工复核。未对效率收益做实测。
