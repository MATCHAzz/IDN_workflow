---
name: data-quality-check
description: Inspect the synthetic Indonesia LiveOps snapshot and check identities, joins, coverage and payment reconciliation before analysis or after suspected missing data.
---

# Data quality

从项目根目录调用 `.venv/bin/python -m liveops call ... --run-id <本任务ID> --args-file <参数JSON>`。

get_data_profile确认快照范围后，可调用read_business_knowledge(topic=data_quality_check)加载共同约束与质量规则；不清楚的术语按[知识目录](../../knowledge/README.md)检索并用entry_ids补读。

- `get_data_profile {}`：确认快照范围、样本量和时区；不代表质量已经通过。
- `check_data_quality {"start_date":"YYYY-MM-DD","end_date":"YYYY-MM-DD"}`：检查主键重复/空值、孤儿外键、每日覆盖、有效日期/维度、金额/状态、成功尝试与交易逐笔一致、付款用户当日观看集合。
- `quality_status=failed` 或工具 error 时停止下游分析和导出；引用 failed checks 与证据路径，不把缺数当零。本合成快照约定每天都有观看、尝试和成功交易，空日判为缺数；真实业务需另订完备性契约。

其他数值工具会再次执行门禁，无需手工传“已通过”。工具证据在返回的 `artifact_path`，含 SQL、参数、耗时和 query IDs。
