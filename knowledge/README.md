# LiveOps 业务知识库

本目录保存业务知识，不执行查询。Agent读取相关文件后编写SQL，再提交execute_readonly_sql；工具不会根据问题自动选择SQL模板。

| 文件 | 内容 |
| --- | --- |
| schema.json | 可查询的逻辑数据源、字段、粒度与关联关系 |
| metrics.json | 五项指标的定义、单位、空值和去重要求 |
| rules.md | 周报、活动、助推与异常分析规则 |
| sql_examples/ | 经执行核对的SQL参考；允许按问题修改，不是后台自动套用的程序 |

可执行阈值继续以config/operations_metrics.json为唯一来源，read_business_knowledge会将它与本目录一起返回，并计算knowledge_id。指标/规则/SQL示例改变后，旧证据不能混入新报告。

SQLite是当前执行方言。将来换Hive需要替换连接器、验证SQL方言，不应将SQLite日期表达式直接复制到Hive。这里没有向量检索；文件较少，按任务读取即可。
