"""Replay a reviewable Agent-authored SQL plan, without pretending to interpret language."""
import json
import uuid
from pathlib import Path

from .knowledge import contract,ROOT
from .store import ToolError,Store
from .tools import ToolRegistry


def run_plan(plan_path,run_id=None,data_dir=None,output_dir=None):
    plan_path=Path(plan_path).resolve()
    plan=json.loads(plan_path.read_text())
    if not isinstance(plan,dict) or not isinstance(plan.get("queries"),list) or not 1<=len(plan["queries"])<=12:
        raise ToolError("INVALID_PLAN","计划需queries数组，包含1到12条SQL")
    if plan.get("workflow") not in {"weekly_report","campaign_review","traffic_boost_update","ad_hoc"}:
        raise ToolError("INVALID_PLAN","计划缺少合法workflow")
    notes=plan.get("notes",{})
    if not isinstance(notes,dict) or set(notes)-{"observations","hypotheses","next_checks"} or any(not isinstance(v,list) or any(not isinstance(t,str) for t in v) for v in notes.values()):
        raise ToolError("INVALID_PLAN","notes需定性文字数组")
    registry=ToolRegistry(data_dir,output_dir)
    run_id=run_id or "sql-"+uuid.uuid4().hex[:12]
    import re,hashlib
    if not isinstance(run_id,str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}",run_id):
        raise ToolError("INVALID_RUN_ID","非法run_id")
    loaded=[]
    for query in plan["queries"]:
        if not isinstance(query,dict) or ("sql" in query)==("sql_file" in query):
            raise ToolError("INVALID_PLAN","每条查询需sql或sql_file，二选一")
        if set(query)-{"sql","sql_file","result_kind","window","label","parameters","filters","only_if_alerts"} or not isinstance(query.get("only_if_alerts",False),bool):
            raise ToolError("INVALID_PLAN","查询项含不支持的参数")
        item=dict(query)
        if "sql_file" in item:
            path=(plan_path.parent/item.pop("sql_file")).resolve()
            if path.suffix!=".sql" or not (path.is_relative_to(ROOT) or path.is_relative_to(plan_path.parent)):
                raise ToolError("INVALID_SQL_FILE","SQL文件需在项目或计划所在目录中，扩展名为.sql")
            item["sql"]=path.read_text()
        loaded.append(item)
    source=Store(registry.data_dir/"liveops.sqlite")
    try:
        snapshot_id=source.metadata()["snapshot_id"]
    finally:
        source.close()
    request={"plan":plan,"sql":loaded,"knowledge_id":contract()["knowledge_id"],"snapshot_id":snapshot_id}
    identity=hashlib.sha256(json.dumps(request,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    directory=registry.output_dir/"runs"/run_id
    marker=directory/"plan_request.json"
    if marker.exists():
        previous=json.loads(marker.read_text())
        if previous["identity"]!=identity:
            raise ToolError("RUN_ID_CONFLICT","同run_id不能重放不同计划、SQL或知识版本")
        state_path=directory/"workflow_state.json"
        if state_path.exists():
            state=json.loads(state_path.read_text())
            if state["status"]=="completed":
                return {**state,"idempotent_replay":True}
        raise ToolError("RUN_INCOMPLETE","保留失败记录，请换新run_id重跑")
    if directory.exists() and any(directory.iterdir()):
        raise ToolError("RUN_ID_CONFLICT","run_id已有其它调用记录，请换新ID")
    directory.mkdir(parents=True,exist_ok=True)
    with marker.open("x",encoding="utf-8") as file:
        json.dump({"identity":identity,"request":request},file,ensure_ascii=False,indent=2)
    (directory/"agent_plan.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2)+"\n")

    def call(name,args):
        response=registry.call(name,args,run_id)
        if response["status"]!="ok":
            (directory/"plan_failure.json").write_text(json.dumps(response,ensure_ascii=False,indent=2)+"\n")
            raise ToolError(response["error"]["code"],response["error"]["message"])
        return response

    call("get_data_profile",{})
    call("read_business_knowledge",{"topic":plan["workflow"]})
    arguments={k:plan[k] for k in ("workflow","report_date","campaign_id","streamer_tier","start_date","end_date") if k in plan}
    context=call("prepare_analysis",arguments)
    evidence_ids=[]
    alerts=False
    for item in loaded:
        item=dict(item)
        only_if_alerts=item.pop("only_if_alerts",False)
        if only_if_alerts and not alerts:
            continue
        response=call("execute_readonly_sql",{"plan_evidence_id":context["evidence_id"],"knowledge_id":context["knowledge_id"],**item})
        evidence_ids.append(response["evidence_id"])
        alerts=alerts or any(row.get("is_anomaly")==1 for row in response["result"]["rows"])
    assembled=call("assemble_analysis",{"plan_evidence_id":context["evidence_id"],"query_evidence_ids":evidence_ids})
    # Qualitative notes reference the assembled, already validated evidence.
    notes={category:[{"text":text,"evidence_ids":[assembled["evidence_id"]]} for text in values]
           for category,values in plan.get("notes",{}).items()}
    exported=call("export_report",{"date":context["result"]["report_date"],"evidence_ids":[assembled["evidence_id"]],"notes":notes})
    delivery=call("prepare_delivery",{"analysis_evidence_id":assembled["evidence_id"],"report_evidence_id":exported["evidence_id"]})
    return {**delivery["result"],"idempotent_replay":False,
            "note":"重放的是Agent已编写并保存的SQL计划；此命令不调用模型、不理解自然语言。"}
