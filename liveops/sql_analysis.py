"""Task context and typed result assembly; no business metric SQL is generated here."""
import json
import math
import re
from datetime import date,timedelta

from . import validation,knowledge
from .validation import validate_scope
from .store import ToolError

TITLES={"weekly_report":"周报更新","campaign_review":"活动复盘","traffic_boost_update":"主播流量助推更新","ad_hoc":"自助问数"}


def evidence(directory,eid):
    if not isinstance(eid,str) or not re.fullmatch(r"e\d{4}",eid):
        raise ToolError("INVALID_EVIDENCE","非法evidence_id")
    path=directory/(eid+".json")
    if not path.is_file():
        raise ToolError("MISSING_EVIDENCE",f"找不到{eid}")
    try:
        value=json.loads(path.read_text())
    except ValueError:
        raise ToolError("INVALID_EVIDENCE","证据尚未完成或JSON无效") from None
    if value["status"]!="ok":
        raise ToolError("INVALID_EVIDENCE","不能使用失败调用")
    return value


def prepare(store,meta,workflow,report_date=None,campaign_id=None,streamer_tier=None,start_date=None,end_date=None):
    if workflow not in TITLES:
        raise ToolError("UNKNOWN_WORKFLOW","不支持的流程")
    if meta.get("generator_version")!="operations-v2":
        raise ToolError("SOURCE_UPGRADE_REQUIRED","动态SQL业务分析需要operations-v2快照")
    filters={k:v for k,v in {"campaign_id":campaign_id,"streamer_tier":streamer_tier}.items() if v is not None}
    validate_scope(store,streamer_tier,campaign_id)
    if workflow=="ad_hoc":
        if report_date is not None:
            raise ToolError("INVALID_ARGUMENTS","自助问数使用start_date/end_date，不使用report_date")
        start,end=validation.validate_range(start_date,end_date,meta)
        record=None
    elif start_date is not None or end_date is not None:
        raise ToolError("INVALID_ARGUMENTS","固定周期任务使用report_date或活动配置，自定义日期仅用于ad_hoc")
    elif workflow=="campaign_review":
        if not campaign_id or report_date is not None:
            raise ToolError("INVALID_ARGUMENTS","活动复盘需campaign_id，日期取活动配置")
        record=store.query("analysis_campaign_context","SELECT name,start_date,end_date FROM campaigns WHERE campaign_id=:campaign",{"campaign":campaign_id})[0]
        start,end=validation.validate_range(record["start_date"],record["end_date"],meta)
    else:
        if campaign_id is not None:
            raise ToolError("INVALID_ARGUMENTS","周报/助推不使用campaign_id")
        end,_=validation.validate_range(report_date,report_date,meta)
        start=end-timedelta(days=6)
        record=None
    previous_end=start-timedelta(days=1)
    previous_start=previous_end-timedelta(days=(end-start).days)
    has_baseline=workflow in {"weekly_report","campaign_review"}
    validation.require_quality(store,(previous_start if has_baseline else start).isoformat(),end.isoformat(),meta)
    return {"workflow":workflow,"title":TITLES[workflow],"report_date":end.isoformat(),
            "date_range":[start.isoformat(),end.isoformat()],
            "baseline_range":[previous_start.isoformat(),previous_end.isoformat()] if has_baseline else None,
            "previous_snapshot_date":(end-timedelta(days=1)).isoformat(),"filters":filters,"campaign":record,
            "knowledge_id":knowledge.contract()["knowledge_id"],
            "required_results":["metrics","comparison"] if has_baseline else ["metrics","boost"] if workflow=="traffic_boost_update" else ["metrics"],
            "note":"Agent根据知识库编写SQL，prepare_analysis只确定日期/名单与所需结果，不生成业务查询。"}


def numeric(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)


def validate_rows(rows,kind,contract):
    metrics=contract["metrics"]
    if kind not in {"metrics","comparison","boost","table"}:
        raise ToolError("INVALID_RESULT_KIND","result_kind仅支持metrics/comparison/boost/table")
    if kind=="table":
        return
    if not rows:
        raise ToolError("EMPTY_ANALYSIS","核心指标、比较或助推清单不能为空")
    seen=set()
    for row in rows:
        if kind in {"metrics","boost"}:
            required=set(metrics)|({"dimension"} if kind=="metrics" else {"streamer_id","streamer_tier","eligible","previous_units","suggested_units","delta_units","action","reason"})
            if not required<=row.keys():
                raise ToolError("RESULT_SCHEMA","结果缺少要求的指标或维度列")
            for key in metrics:
                if not numeric(row[key]) or row[key]<0:
                    raise ToolError("RESULT_SCHEMA",f"{key}必须为非负有限数值")
                if key in {"gift_amount_idr","effective_live_days","viewer_uv"} and int(row[key])!=row[key]:
                    raise ToolError("RESULT_SCHEMA",f"{key}必须为整数")
            identity=row["dimension"] if kind=="metrics" else row["streamer_id"]
            if kind=="boost":
                if not isinstance(row["streamer_id"],int) or row["streamer_tier"] not in {"head","mid","tail"}:
                    raise ToolError("RESULT_SCHEMA","主播ID或层级非法")
                if row["eligible"] not in (0,1) or row["action"] not in {"increase","decrease","keep","review_missing_snapshot"}:
                    raise ToolError("RESULT_SCHEMA","助推资格或action非法")
                if not numeric(row["suggested_units"]) or row["suggested_units"]<0:
                    raise ToolError("RESULT_SCHEMA","助推建议额度非法")
                if row["previous_units"] is not None:
                    if not numeric(row["previous_units"]) or row["previous_units"]<0 or not numeric(row["delta_units"]) or not math.isclose(row["delta_units"],row["suggested_units"]-row["previous_units"]):
                        raise ToolError("RESULT_RECONCILIATION","助推额度差值不一致")
                if not isinstance(row["reason"],str):
                    raise ToolError("RESULT_SCHEMA","助推原因必须为字符串")
        else:
            if not {"dimension","metric","current","baseline","delta","relative_change","is_anomaly","status"}<=row.keys() or row["metric"] not in metrics:
                raise ToolError("RESULT_SCHEMA","比较结果不符合知识库契约")
            identity=(row["dimension"],row["metric"])
            if not numeric(row["current"]) or not numeric(row["baseline"]) or row["current"]<0 or row["baseline"]<0 or not numeric(row["delta"]) or not math.isclose(row["delta"],row["current"]-row["baseline"],abs_tol=1e-8):
                raise ToolError("RESULT_RECONCILIATION","比较结果差值不一致")
            expected=row["delta"]/row["baseline"] if row["baseline"] else None
            if expected is None and row["relative_change"] is not None or expected is not None and (not numeric(row["relative_change"]) or not math.isclose(expected,row["relative_change"],abs_tol=1e-8)):
                raise ToolError("RESULT_RECONCILIATION","相对变化不一致")
            if row["status"] not in {"ok","zero_baseline","small_sample"} or row["is_anomaly"] not in (None,0,1):
                raise ToolError("RESULT_SCHEMA","告警状态非法")
            if row["status"]!="ok" and row["is_anomaly"] is not None:
                raise ToolError("RESULT_SCHEMA","无法判断时告警必须为NULL")
        try:
            if identity in seen:
                raise ToolError("DUPLICATE_RESULT","结果维度重复")
            seen.add(identity)
        except TypeError:
            raise ToolError("RESULT_SCHEMA","维度必须为字符串或数字") from None


def assemble(directory,meta,plan_evidence_id,query_evidence_ids):
    plan_env=evidence(directory,plan_evidence_id)
    if plan_env["tool"]!="prepare_analysis":
        raise ToolError("INVALID_PLAN","需要prepare_analysis证据")
    plan=plan_env["result"]
    contract=knowledge.contract()
    if not isinstance(query_evidence_ids,list) or not query_evidence_ids:
        raise ToolError("INVALID_EVIDENCE","需本次SQL查询证据列表")
    sources=[]
    for eid in dict.fromkeys([plan_evidence_id,*query_evidence_ids]):
        env=evidence(directory,eid)
        if env.get("snapshot_id")!=meta["snapshot_id"] or env.get("knowledge_id")!=contract["knowledge_id"]:
            raise ToolError("KNOWLEDGE_MISMATCH","快照或知识库已改变，请重新分析")
        if eid!=plan_evidence_id:
            if env["tool"]!="execute_readonly_sql" or env["arguments"].get("plan_evidence_id")!=plan_evidence_id:
                raise ToolError("INVALID_EVIDENCE","SQL证据不属于本任务计划")
            sources.append(env)
    current=[e for e in sources if e["result"]["result_kind"]=="metrics" and e["result"]["window"]=="current" and e["result"]["filters"]==plan["filters"] and len(e["result"]["rows"])==1 and e["result"]["rows"][0]["dimension"]=="all"]
    if len(current)!=1:
        raise ToolError("MISSING_CORE_METRICS","需唯一的本期整体五项指标，dimension='all'")
    result={"workflow":plan["workflow"],"title":plan["title"],"date_range":plan["date_range"],"baseline_range":plan["baseline_range"],
            "current":{"rows":[{"dimension":r["dimension"],"metrics":{k:r[k] for k in contract["metrics"]}} for r in current[0]["result"]["rows"]]},
            "source_evidence_ids":[plan_evidence_id,*query_evidence_ids],"source_queries":sources,
            "knowledge_id":contract["knowledge_id"],"analysis_mode":"agent_generated_sql", "warnings":["SQL访问与结果形状已校验，不等于自动证明业务口径正确；解释需人工审阅。"]}
    if plan["baseline_range"]:
        comparisons=[row for e in sources if e["result"]["result_kind"]=="comparison" and e["result"]["window"]=="comparison" and e["result"]["filters"]==plan["filters"] for row in e["result"]["rows"]]
        overall=[r for r in comparisons if r["dimension"]=="all"]
        if len(overall)!=len(contract["metrics"]) or {r["metric"] for r in overall}!=set(contract["metrics"]):
            raise ToolError("MISSING_COMPARISON","需完整整体五指标比较")
        current_metrics=current[0]["result"]["rows"][0]
        if any(not math.isclose(r["current"],current_metrics[r["metric"]],abs_tol=1e-8) for r in overall):
            raise ToolError("RESULT_RECONCILIATION","整体本期指标与比较查询的本期值不一致")
        result["operations_comparisons"]=[{**r,"label":contract["metrics"][r["metric"]]["label"],"unit":contract["metrics"][r["metric"]]["unit"],"is_anomaly":None if r["is_anomaly"] is None else bool(r["is_anomaly"])} for r in overall]
        result["dimension_comparisons"]=[{**r,"label":contract["metrics"][r["metric"]]["label"],"is_anomaly":None if r["is_anomaly"] is None else bool(r["is_anomaly"])} for r in comparisons if r["dimension"]!="all"]
    elif plan["workflow"]=="traffic_boost_update":
        boosts=[e for e in sources if e["result"]["result_kind"]=="boost" and e["result"]["filters"]==plan["filters"]]
        if len(boosts)!=1:
            raise ToolError("MISSING_BOOST_LIST","需唯一的完整助推查询结果")
        result["candidate_rows"]=boosts[0]["result"]["rows"]
    return result
