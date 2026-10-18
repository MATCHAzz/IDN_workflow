"""Parse Agent SQL, restrict sources, then execute a scoped read-only statement."""
import math
import sqlite3

from .store import Store,ToolError

SOURCES={"watch_events","gift_events","broadcast_days","streamer_profiles","boost_snapshots","campaign_members"}
FUNCTIONS={"sum","count","min","max","avg","coalesce","round","abs","nullif","date","strftime","julianday","typeof","length"}


def parse_query(sql):
    try:
        import sqlglot
        from sqlglot import exp
        from sqlglot.optimizer.scope import traverse_scope
    except ImportError:
        raise ToolError("DEPENDENCY_MISSING","请使用.venv/bin/python，或安装requirements.txt中的SQLGlot") from None
    if not isinstance(sql,str) or not sql.strip() or len(sql)>40000:
        raise ToolError("INVALID_SQL","SQL必须为非空字符串，最多40000字符")
    try:
        statements=sqlglot.parse(sql,read="sqlite")
    except (sqlglot.errors.ParseError,sqlglot.errors.TokenError,RecursionError) as exc:
        raise ToolError("SQL_PARSE_ERROR",str(exc)) from None
    if len(statements)!=1 or not isinstance(statements[0],(exp.Select,exp.Union)):
        raise ToolError("READ_ONLY_SQL","只接受单条SELECT或非递归WITH查询")
    tree=statements[0]
    denied={"insert","update","delete","create","drop","alter","command","pragma","attach","detach","transaction","commit","rollback","into","merge","copy","grant","revoke","load_data"}
    for index,node in enumerate(tree.walk()):
        if index>4000:
            raise ToolError("SQL_COMPLEXITY_LIMIT","SQL语法树过大，请简化查询")
        if node.key in denied:
            raise ToolError("READ_ONLY_SQL","SQL中包含不允许的操作")
        if isinstance(node,exp.With) and node.args.get("recursive"):
            raise ToolError("RECURSIVE_SQL_DENIED","不允许递归查询")
        if isinstance(node,exp.CTE) and node.alias_or_name.lower() in SOURCES:
            raise ToolError("RESERVED_SOURCE","不能覆盖工具提供的逻辑数据源")
        if isinstance(node,exp.Star) and not isinstance(node.parent,exp.Count):
            raise ToolError("STAR_DENIED","请明确列名，不支持SELECT *")
        if isinstance(node,exp.Func):
            name=node.name.lower() if isinstance(node,exp.Anonymous) else node.sql_name().lower()
            if name not in FUNCTIONS|{"case","if","cast","and","or"}:
                raise ToolError("FUNCTION_DENIED",f"不支持的SQL函数：{name}")
        if isinstance(node,exp.Column) and node.name.lower()=="viewer_id":
            parent=node.parent
            if not (isinstance(parent,exp.Distinct) and isinstance(parent.parent,exp.Count) and len(parent.expressions)==1 and parent.expressions[0] is node):
                raise ToolError("USER_DETAIL_DENIED","viewer_id仅允许COUNT(DISTINCT viewer_id)，不能输出、筛选或关联用户明细")
    try:
        scopes=traverse_scope(tree)
        for scope in scopes:
            direct=[]
            for source in scope.sources.values():
                if isinstance(source,exp.Table):
                    if source.db or source.catalog or source.name.lower() not in SOURCES:
                        raise ToolError("SOURCE_DENIED","只允许知识库中的逻辑数据源")
                    direct.append(source.name.lower())
            if len(set(direct)&{"watch_events","gift_events","broadcast_days"})>1:
                raise ToolError("MULTI_FACT_JOIN","多个明细事实源必须分别聚合后再关联，避免重复计数")
            if set(direct)&{"watch_events","gift_events"}:
                aggregates=[n for n in scope.expression.find_all(exp.AggFunc) if n.find_ancestor(exp.Select) is scope.expression]
                if not aggregates:
                    raise ToolError("AGGREGATION_REQUIRED","观看/打赏明细必须聚合，不能直接返回事件记录")
    except ToolError:
        raise
    except Exception as exc:
        raise ToolError("SQL_SCOPE_ERROR","无法确认查询作用域："+str(exc)) from None
    if not any(isinstance(t,exp.Table) and t.name.lower() in SOURCES for t in tree.find_all(exp.Table)):
        raise ToolError("SOURCE_REQUIRED","查询必须引用至少一个知识库数据源")
    return tree


def bind_scope(tree,parameters,filters):
    from sqlglot import exp,parse_one
    conditions=[]
    if filters.get("streamer_tier") is not None:
        conditions.append("tier=:scope_tier")
        parameters["scope_tier"]=filters["streamer_tier"]
    if filters.get("streamer_id") is not None:
        conditions.append("streamer_id=:scope_streamer")
        parameters["scope_streamer"]=filters["streamer_id"]
    if filters.get("campaign_id") is not None:
        conditions.append("streamer_id IN (SELECT streamer_id FROM campaign_streamers WHERE campaign_id=:scope_campaign)")
        parameters["scope_campaign"]=filters["campaign_id"]
    profile="SELECT streamer_id,tier,category FROM streamers"+(" WHERE "+" AND ".join(conditions) if conditions else "")
    definitions={
        "streamer_profiles":profile,
        "watch_events":"SELECT date,user_id AS viewer_id,streamer_id,duration_seconds FROM view_sessions WHERE date BETWEEN :start_date AND :end_date AND streamer_id IN (SELECT streamer_id FROM streamer_profiles)",
        "gift_events":"SELECT date,streamer_id,amount_idr FROM transactions WHERE date BETWEEN :start_date AND :end_date AND streamer_id IN (SELECT streamer_id FROM streamer_profiles)",
        "broadcast_days":"SELECT date,streamer_id,live_seconds FROM streamer_daily WHERE date BETWEEN :start_date AND :end_date AND streamer_id IN (SELECT streamer_id FROM streamer_profiles)",
        "boost_snapshots":"SELECT date,streamer_id,allocated_units FROM traffic_boost_daily WHERE date BETWEEN :start_date AND :end_date AND streamer_id IN (SELECT streamer_id FROM streamer_profiles)",
        "campaign_members":"SELECT campaign_id,streamer_id FROM campaign_streamers WHERE streamer_id IN (SELECT streamer_id FROM streamer_profiles)",
    }
    ctes=[exp.CTE(this=parse_one(sql,read="sqlite"),alias=exp.TableAlias(this=exp.to_identifier(name))) for name,sql in definitions.items()]
    existing=tree.args.get("with_")
    tree.set("with_",exp.With(expressions=ctes+(existing.expressions if existing else [])))
    return tree.sql(dialect="sqlite")


class GeneratedSQLStore(Store):
    @staticmethod
    def _authorize(action,arg1,arg2,database,source):
        if action in (sqlite3.SQLITE_SELECT,sqlite3.SQLITE_RECURSIVE):
            return sqlite3.SQLITE_OK
        if action==sqlite3.SQLITE_READ:
            return sqlite3.SQLITE_OK if arg1 in {"streamers","view_sessions","transactions","streamer_daily","traffic_boost_daily","campaign_streamers"} else sqlite3.SQLITE_DENY
        if action==sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK if (arg2 or "").lower() in FUNCTIONS else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_DENY

    def execute_generated(self,sql,parameters,filters):
        tree=parse_query(sql)
        prepared=bind_scope(tree,parameters,filters)
        try:
            rows=self.query("agent_generated_sql",prepared,parameters)
        except sqlite3.Error as exc:
            raise ToolError("SQL_EXECUTION_ERROR",str(exc)) from None
        for row in rows:
            for value in row.values():
                if isinstance(value,float) and not math.isfinite(value):
                    raise ToolError("NONFINITE_RESULT","查询包含无效数值")
        return rows,prepared
