---
name: root-cause-drilldown
description: Choose a relevant streamer tier or streamer after a LiveOps change, author additional aggregate SQL from the shared knowledge, and separate facts from possible explanations.
---

# SQL下钻

先读已有比较结果，确认窗口、名单、质量和知识版本，再选与变化有关的层级或主播。保持同prepare_analysis计划；通过execute_readonly_sql的filters进一步缩小范围，不能替换计划已有名单。

从[指标与表结构](../../knowledge/README.md)编写追加SQL，result_kind=table用于补充聚合、comparison用于比较，所有差值由SQL计算。先看有效直播天数/直播时长，再看观看时长/观众数，最后看打赏。独立计算UV，多个事实表先聚合。

查询方向由Agent根据结果决定，不固定跑满所有维度。没有足够数据时说明缺口；事实、假设和下一步分开，不能证明活动因果。把实际执行的新证据一并交assemble_analysis，不仅保留结论文字。
