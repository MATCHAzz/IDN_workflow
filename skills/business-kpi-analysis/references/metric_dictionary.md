# 指标字典入口

当前定义统一保存在[knowledge/metrics.json](../../../knowledge/metrics.json)，表结构见[knowledge/schema.json](../../../knowledge/schema.json)，任务规则见[knowledge/rules.md](../../../knowledge/rules.md)。可执行阈值来自config/operations_metrics.json，由read_business_knowledge一并返回。

不在本文件重复维护另一份指标定义。先读取知识再写SQL；Python保留query_gift_total作为单一固定业务查询对照。
