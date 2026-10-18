"""Agent-facing SQL tools. The model supplies SQL; these tools never select business SQL."""
import json
import math
import re

from . import validation,knowledge,sql_analysis,report
from .validation import validate_scope
from .simple_query import query_gift_total
from .sql_guard import GeneratedSQLStore
from .store import ToolError


class SQLToolsMixin:
    def read_business_knowledge(self,store,meta,topic="metrics"):
        return knowledge.read(topic)

    def get_metric_dictionary(self,store,meta):
        return knowledge.contract()

    def prepare_analysis(self,store,meta,workflow,report_date=None,campaign_id=None,streamer_tier=None,start_date=None,end_date=None):
        return sql_analysis.prepare(store,meta,workflow,report_date,campaign_id,streamer_tier,start_date,end_date)

    def query_gift_total(self,store,meta,start_date,end_date):
        return query_gift_total(store,meta,start_date,end_date)

    def execute_readonly_sql(self,store,meta,plan_evidence_id,knowledge_id,sql,result_kind="table",window="current",parameters=None,filters=None,label="SQL分析"):
        context=sql_analysis.evidence(self._run_dir,plan_evidence_id)
        contract=knowledge.contract()
        if context["tool"]!="prepare_analysis" or context.get("snapshot_id")!=meta["snapshot_id"]:
            raise ToolError("INVALID_PLAN","计划必须来自本run当前快照的prepare_analysis")
        if knowledge_id!=contract["knowledge_id"] or context.get("knowledge_id")!=knowledge_id:
            raise ToolError("KNOWLEDGE_MISMATCH","知识库已改变，请重新读取知识并准备任务")
        plan=context["result"]
        if window not in {"current","comparison"} or window=="comparison" and not plan["baseline_range"]:
            raise ToolError("INVALID_WINDOW","不支持的查询窗口")
        if result_kind=="comparison" and window!="comparison":
            raise ToolError("INVALID_WINDOW","比较查询必须使用comparison窗口")
        if result_kind in {"metrics","boost"} and window!="current":
            raise ToolError("INVALID_WINDOW","本期指标和助推查询使用current窗口")
        active_filters=dict(plan["filters"])
        if filters is not None:
            if not isinstance(filters,dict) or set(filters)-{"streamer_tier","streamer_id","campaign_id"}:
                raise ToolError("INVALID_FILTER","非法追加筛选")
            for key,value in filters.items():
                if key in active_filters and value!=active_filters[key]:
                    raise ToolError("SCOPE_EXPANSION_DENIED","追加查询不能改变任务已确定的范围")
                if value is None:
                    raise ToolError("INVALID_FILTER","追加筛选不能为空")
                active_filters[key]=value
        validate_scope(store,active_filters.get("streamer_tier"),active_filters.get("campaign_id"),active_filters.get("streamer_id"))
        start=plan["baseline_range"][0] if window=="comparison" else plan["date_range"][0]
        end=plan["date_range"][1]
        validation.require_quality(store,start,end,meta)
        cfg=contract["rules"]
        bindings={"start_date":start,"end_date":end,"current_start":plan["date_range"][0],"current_end":end,
                  "baseline_start":plan["baseline_range"][0] if plan["baseline_range"] else None,
                  "baseline_end":plan["baseline_range"][1] if plan["baseline_range"] else None,
                  "report_date":plan["report_date"],"previous_snapshot_date":plan["previous_snapshot_date"],
                  "min_live_seconds":cfg["effective_live_day"]["min_live_seconds"],
                  "min_watch_seconds":cfg["effective_live_day"]["min_watch_seconds"],
                  "drop_threshold":cfg["monitoring"]["relative_drop_threshold"],"min_viewers":cfg["monitoring"]["minimum_viewers_for_alert"],
                  "boost_days":cfg["traffic_boost"]["min_effective_days_7d"],"boost_viewers":cfg["traffic_boost"]["min_viewer_uv_7d"],
                  "boost_units":cfg["traffic_boost"]["suggested_units_per_streamer"]}
        parameters={} if parameters is None else parameters
        if not isinstance(parameters,dict):
            raise ToolError("INVALID_PARAMETERS","parameters需为JSON对象")
        for key,value in parameters.items():
            if not isinstance(key,str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}",key) or key in bindings or key.startswith("scope_"):
                raise ToolError("RESERVED_PARAMETER","不能覆盖工具注入的日期、口径和范围参数")
            if not (value is None or isinstance(value,(str,int,float))) or isinstance(value,float) and not math.isfinite(value) or isinstance(value,str) and len(value)>1000:
                raise ToolError("INVALID_PARAMETERS","只接受有限数值、短字符串或null参数")
            bindings[key]=value
        if not isinstance(label,str) or len(label)>100:
            raise ToolError("INVALID_LABEL","查询标题最多100字")
        generated=GeneratedSQLStore(self.data_dir/"liveops.sqlite")
        try:
            rows,prepared=generated.execute_generated(sql,bindings,active_filters)
        finally:
            store.queries.extend(generated.queries)
            generated.close()
        sql_analysis.validate_rows(rows,result_kind,contract)
        if result_kind=="boost":
            clause,scope_params=validate_scope(store,active_filters.get("streamer_tier"),active_filters.get("campaign_id"),active_filters.get("streamer_id"))
            expected=store.query("boost_expected_cohort","SELECT s.streamer_id FROM streamers s WHERE 1=1 "+clause,scope_params)
            if {r["streamer_id"] for r in rows}!={r["streamer_id"] for r in expected}:
                raise ToolError("INCOMPLETE_BOOST_LIST","助推清单必须覆盖计划范围内完整主播名单")
        return {"title":label,"date_range":[start,end],"window":window,"result_kind":result_kind,
                "filters":active_filters,"rows":rows,"columns":list(rows[0]) if rows else [],"knowledge_id":knowledge_id,
                "submitted_sql":sql,"prepared_sql":prepared,"bound_parameters":bindings,
                "validation":"单条只读SQL、限定逻辑数据源、日期和主播范围、聚合限制、输出契约；不证明业务语义正确。",
                "warnings":[] if rows else ["查询无结果，不能把缺结果解释为零或正常。"]}

    def assemble_analysis(self,store,meta,plan_evidence_id,query_evidence_ids):
        result=sql_analysis.assemble(self._run_dir,meta,plan_evidence_id,query_evidence_ids)
        validation.require_quality(store,result["date_range"][0],result["date_range"][1],meta)
        return result

    def export_report(self,store,meta,date,evidence_ids,notes=None):
        validation.require_quality(store,date,date,meta)
        if not isinstance(evidence_ids,list) or not evidence_ids:
            raise ToolError("INVALID_EVIDENCE","需要分析证据列表")
        for eid in evidence_ids:
            if sql_analysis.evidence(self._run_dir,eid).get("knowledge_id")!=knowledge.contract()["knowledge_id"]:
                raise ToolError("KNOWLEDGE_MISMATCH","默认SQL路径不接受旧知识或旧固定流程证据")
        return report.export(self._run_dir,date,evidence_ids,notes,meta)

    def prepare_delivery(self,store,meta,analysis_evidence_id,report_evidence_id):
        analysis=sql_analysis.evidence(self._run_dir,analysis_evidence_id)
        exported=sql_analysis.evidence(self._run_dir,report_evidence_id)
        kid=knowledge.contract()["knowledge_id"]
        for env in (analysis,exported):
            if env.get("knowledge_id")!=kid or env.get("snapshot_id")!=meta["snapshot_id"]:
                raise ToolError("KNOWLEDGE_MISMATCH","报告、分析与当前知识/快照必须一致")
        if analysis["tool"]!="assemble_analysis" or exported["tool"]!="export_report" or analysis_evidence_id not in exported["arguments"]["evidence_ids"]:
            raise ToolError("INVALID_EVIDENCE","报告必须引用此分析结果")
        result=analysis["result"]
        validation.require_quality(store,result["date_range"][0],result["date_range"][1],meta)
        draft={"title":result["title"],"run_id":self._run_dir.name,"date_range":result["date_range"],
               "artifacts":exported["result"]["paths"],"status":"draft_not_sent","destination":None,"scheduled_at":None,
               "analysis_mode":"agent_generated_sql","knowledge_id":kid}
        path=self._run_dir/"delivery_draft.json"
        path.write_text(json.dumps(draft,ensure_ascii=False,indent=2)+"\n")
        state={"run_id":self._run_dir.name,"status":"completed","human_approved":False,
               "request":{"workflow":result["workflow"],"snapshot_id":meta["snapshot_id"],"knowledge_id":kid},
               "analysis_mode":"agent_generated_sql","analysis_evidence_id":analysis_evidence_id,"report_evidence_id":report_evidence_id,
               "report_paths":exported["result"]["paths"],"delivery_draft":str(path.resolve())}
        (self._run_dir/"workflow_state.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
        from .workspace import workspace_index
        return {**state,"workspace_index":workspace_index(self.output_dir)}
