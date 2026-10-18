"""Render numbers exclusively from stored tool evidence; agent adds referenced qualitative notes."""
import html
import json
import csv
from pathlib import Path

from .store import ToolError
from .knowledge import contract


def fmt(value, metric=""):
    if value is None:
        return "未知 / 无法计算"
    if isinstance(value, bool):
        return "是" if value else "否"
    if metric == "relative_change":
        return f"{value:.2%}"
    if isinstance(value, (int, float)):
        return f"{value:,.0f}" if isinstance(value, int) else f"{value:,.2f}"
    return str(value)


def render(target_date, envelopes, notes, run_id):
    report_title=envelopes[0]["result"].get("title","运营指标看板")
    md = [f"# {report_title} · {target_date}", "", "100% 合成数据 · Asia/Jakarta · 内部草稿 · 未对外发送", "",
          f"运行：`{run_id}`；快照：`{envelopes[0]['snapshot_id']}`；口径：`{envelopes[0]['metric_version']}`。", ""]
    panels = []

    def table(headers, rows):
        md.extend(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"])
        md.extend("| " + " | ".join(str(v).replace("|", "\\|") for v in row) + " |" for row in rows)
        md.append("")
        return "<div class='scroll'><table><thead><tr>" + "".join(f"<th>{html.escape(str(h))}</th>" for h in headers) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>" for row in rows) + "</tbody></table></div>"

    for envelope in envelopes:
        result, eid = envelope["result"], envelope["evidence_id"]
        labels={k:(v["label"],v["unit"]) for k,v in contract()["metrics"].items()}
        title = result.get("title", envelope["tool"]) + " · " + eid
        md.extend(["## " + title, ""])
        body = ""
        datasets = []
        if "current" in result:
            datasets.append(("本期核心指标",result["current"]))
        for label,dataset in datasets:
            rows=[]
            for row in dataset["rows"]:
                for key,value in row["metrics"].items():
                    rows.append([str(row["dimension"]),labels[key][0],fmt(value),labels[key][1]])
            md.extend(["### "+label,""])
            body+="<h3>"+label+"</h3>"+table(["分组","指标","数值","单位"],rows)
        if "operations_comparisons" in result:
            md.extend(["对比区间："+" 至 ".join(result["baseline_range"]),""])
            body+="<p>对比区间："+html.escape(" 至 ".join(result["baseline_range"]))+"</p>"
            body+=table(["指标","本期","上期","变化","监控状态"],[[r["label"],fmt(r["current"]),fmt(r["baseline"]),fmt(r["relative_change"],"relative_change"),"下降提醒" if r["is_anomaly"] else "待判断" if r["is_anomaly"] is None else "未触发"] for r in result["operations_comparisons"]])
            bars=[]
            for row in result["operations_comparisons"]:
                change=row["relative_change"]
                if change is None:
                    continue
                width=min(100,abs(change)*100)
                color="#bd4d4d" if change<0 else "#008c83"
                bars.append("<div style='display:grid;grid-template-columns:130px 1fr 85px;gap:10px;align-items:center;margin:10px 0;font-size:13px'><span>"+html.escape(row["label"])+"</span><div style='background:#edf2f7;height:12px;border-radius:6px'><div style='height:12px;border-radius:6px;background:"+color+";width:"+str(width)+"%'></div></div><strong>"+fmt(change,"relative_change")+"</strong></div>")
            body+="<h3>核心指标变化</h3><p style='font-size:12px;color:#59768d'>相同长度窗口对比；色条按变化幅度显示，超过百分之百时封顶。</p>"+"".join(bars)
        if "dimension_comparisons" in result:
            body+=table(["层级","指标","变化","状态"],[[r["dimension"],r["label"],fmt(r["relative_change"],"relative_change"),"下降提醒" if r["is_anomaly"] else "待判断" if r["is_anomaly"] is None else "未触发"] for r in result["dimension_comparisons"]])
        if "candidate_rows" in result:
            md.extend(["助推清单见同目录 traffic_boost_candidates.csv；仅为待审核草稿。",""])
            body+="<p>待审核助推更新清单：<a href='traffic_boost_candidates.csv'>下载完整CSV</a></p>"
            body+=table(["主播","层级","有效天数","观看UV","原额度","建议额度","操作"],[[r["streamer_id"],r["streamer_tier"],r["effective_live_days"],r["viewer_uv"],fmt(r["previous_units"]),r["suggested_units"],r["action"]] for r in result["candidate_rows"]])
        if envelope["tool"] in {"execute_readonly_sql","query_gift_total"}:
            raw=result.get("rows",[])
            if raw:
                columns=list(raw[0])
                body+=table(columns,[[fmt(row.get(key),"relative_change" if key=="relative_change" else key) for key in columns] for row in raw])
        for source in result.get("source_queries",[]):
            query=source["result"]
            caption=query.get("title","SQL查询")+" · "+source["evidence_id"]
            md.extend(["### "+caption,"","```sql",query["submitted_sql"],"```","",f"[查询结果与实际执行证据]({source['evidence_id']}.json)",""])
            body+="<details><summary>Agent生成SQL："+html.escape(caption)+"</summary><pre>"+html.escape(query["submitted_sql"])+"</pre><a href='"+source["evidence_id"]+".json'>查看结果、限定范围与实际执行SQL</a></details>"
            if query["result_kind"]=="table" and query["rows"]:
                columns=list(query["rows"][0])
                body+=table(columns,[[fmt(row.get(k)) for k in columns] for row in query["rows"]])
        if "quality_status" in result:
            passed = sum(c["passed"] for c in result["checks"])
            text = f"质量门禁：{result['quality_status']}；{passed}/{len(result['checks'])} 项通过。"
            md.extend([text, ""])
            body += "<p>" + html.escape(text) + "</p>"
        for warning in result.get("warnings", []):
            md.extend(["> " + warning, ""])
            body += "<p class='warning'>" + html.escape(warning) + "</p>"
        md.extend([f"[原始工具结果与 SQL 证据]({eid}.json)", "", "查询：" + ", ".join(f"`{qid}`" for qid in envelope["query_ids"]), ""])
        body += f"<details><summary>查看调用与查询证据</summary><p>{html.escape(envelope['skill'])} · {envelope['elapsed_ms']} ms</p><a href='{eid}.json'>打开原始 JSON / SQL</a><pre>" + html.escape(json.dumps({"arguments": envelope["arguments"], "query_ids": envelope["query_ids"]}, ensure_ascii=False, indent=2)) + "</pre></details>"
        panels.append("<section><h2>" + html.escape(title) + "</h2>" + body + "</section>")
    names = {"observations": "Agent 观察", "hypotheses": "待验证的解释", "next_checks": "下一步调查"}
    for category, label in names.items():
        if not notes.get(category):
            continue
        md.extend(["## " + label, ""])
        items = []
        for note in notes[category]:
            refs = ", ".join(note["evidence_ids"])
            md.append(f"- {note['text']} [{refs}]")
            items.append("<li>" + html.escape(note["text"]) + " <small>" + html.escape(refs) + "</small></li>")
        md.append("")
        panels.append("<section><h2>" + label + "</h2><ul>" + "".join(items) + "</ul></section>")
    limitation = "仅合成数据与待审核草稿；活动前后变化不证明因果。有效直播门槛见统一指标配置。内部数据系统、实际流量下发与定时推送尚未接入，未实测节省工时。"
    md.extend(["## 分析边界", "", limitation, ""])
    markup = """<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>LiveOps · 运营自动化看板</title><style>
:root{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;color:#152439;background:#eef2f7;line-height:1.6}body{max-width:1160px;margin:0 auto;padding:36px 24px}header{padding:32px;border-radius:20px;background:#122c47;color:#fff}header p{color:#c4d3e2}.badge{display:inline-block;background:#1e526a;padding:4px 12px;border-radius:24px;font-size:13px}h1{font-size:32px;letter-spacing:-1px}h2{font-size:19px}section{background:#fff;margin:20px 0;padding:24px;border:1px solid #dce3eb;border-radius:16px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:13px}th{background:#f0f4f8;text-align:left}td,th{padding:10px;border-bottom:1px solid #e4eaf0;white-space:nowrap}td{font-variant-numeric:tabular-nums}a{color:#007f83}details{margin-top:20px;font-size:13px;color:#486179}summary{cursor:pointer}pre{overflow:auto;background:#f4f7fa;padding:16px}.warning{background:#fff7df;padding:12px;border-radius:8px}footer{color:#52657b;font-size:13px}small{color:#59768d}
</style><header style='padding:18px 24px'><span class='badge'>合成数据 · 内部草稿</span><h1 style='font-size:26px;margin:10px 0'>__TITLE__</h1><p style='margin:4px 0'>__DATE__ · Asia/Jakarta</p></header>__PANELS__<footer>__LIMIT__</footer></html>"""
    markup = markup.replace("__DATE__", html.escape(target_date)).replace("__TITLE__",html.escape(report_title)).replace("__PANELS__", "".join(panels)).replace("__LIMIT__", limitation)
    return "\n".join(md), markup


def export(run_dir: Path, target_date, evidence_ids, notes, meta):
    if not isinstance(evidence_ids, list) or not evidence_ids:
        raise ToolError("INVALID_EVIDENCE", "必须指定本次 run 中的 evidence_ids")
    envelopes = []
    for eid in dict.fromkeys(evidence_ids):
        if not isinstance(eid, str) or len(eid) != 5 or not eid.startswith("e") or not eid[1:].isdigit():
            raise ToolError("INVALID_EVIDENCE", "非法 evidence_id")
        path = run_dir / (eid + ".json")
        if not path.is_file():
            raise ToolError("MISSING_EVIDENCE", f"找不到 {eid}")
        envelope = json.loads(path.read_text())
        if envelope["status"] != "ok" or envelope.get("snapshot_id") != meta["snapshot_id"]:
            raise ToolError("INVALID_EVIDENCE", "不能使用失败调用或其他快照的证据")
        if envelope["tool"] not in {"check_data_quality", "assemble_analysis", "execute_readonly_sql", "query_gift_total"}:
            raise ToolError("INVALID_EVIDENCE", "该工具结果不能作为分析证据")
        args = envelope["arguments"]
        coverage=envelope["result"].get("date_range",[args.get("start_date","9999"),args.get("end_date","0000")])
        if not (args.get("date") == target_date or coverage[0] <= target_date <= coverage[1]):
            raise ToolError("DATE_MISMATCH", "证据日期范围未覆盖报告日期")
        active=contract()
        if envelope.get("config_id")!=active["config_id"]:
            raise ToolError("CONFIG_MISMATCH","指标配置已变化，请重算证据再导出")
        if envelope.get("knowledge_id")!=active["knowledge_id"]:
            raise ToolError("KNOWLEDGE_MISMATCH","知识库已变化，请重新生成分析证据")
        envelopes.append(envelope)
    if not any(e["tool"] != "check_data_quality" for e in envelopes):
        raise ToolError("MISSING_ANALYSIS", "仅有质量检查，缺少分析数值")
    notes = notes or {}
    if not isinstance(notes, dict) or set(notes) - {"observations", "hypotheses", "next_checks"}:
        raise ToolError("INVALID_NOTES", "notes 仅支持 observations, hypotheses, next_checks")
    for items in notes.values():
        if not isinstance(items, list):
            raise ToolError("INVALID_NOTES", "notes 每类应为数组")
        for note in items:
            if not isinstance(note, dict) or set(note) != {"text", "evidence_ids"} or not isinstance(note["text"], str) or len(note["text"]) > 1000:
                raise ToolError("INVALID_NOTES", "备注需 text 与 evidence_ids，最多1000字")
            if any(char.isdecimal() for char in note["text"]):
                raise ToolError("UNVERIFIED_NUMBER", "备注只写定性解释；数字由工具证据自动渲染")
            if not isinstance(note["evidence_ids"], list) or not note["evidence_ids"] or any(ref not in evidence_ids for ref in note["evidence_ids"]):
                raise ToolError("INVALID_NOTES", "每条备注必须引用已选证据")
    markdown, markup = render(target_date, envelopes, notes, run_dir.name)
    # Content-addressed report directory gives repeat requests the same artifact, no external publishing.
    import hashlib
    payload = {"date": target_date, "run_id": run_dir.name, "human_approved": False,
               "evidence": envelopes, "agent_notes": notes, "metric_version": envelopes[0]["metric_version"]}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    report_id = "report-" + hashlib.sha256(canonical.encode()).hexdigest()[:12]
    report_dir = run_dir / report_id
    report_dir.mkdir(exist_ok=True)
    for envelope in envelopes:
        (report_dir / (envelope["evidence_id"] + ".json")).write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n")
        for source_id in envelope["result"].get("source_evidence_ids",[]):
            from .sql_analysis import evidence
            source=evidence(run_dir,source_id)
            (report_dir/(source_id+".json")).write_text(json.dumps(source,ensure_ascii=False,indent=2)+"\n")
    (report_dir / "report.json").write_text(canonical + "\n")
    (report_dir / "report.md").write_text(markdown)
    (report_dir / "report.html").write_text(markup)
    candidates=[e["result"]["candidate_rows"] for e in envelopes if "candidate_rows" in e["result"]]
    if candidates:
        with (report_dir/"traffic_boost_candidates.csv").open("w",newline="",encoding="utf-8-sig") as file:
            writer=csv.DictWriter(file,fieldnames=list(candidates[-1][0]) if candidates[-1] else ["streamer_id"])
            writer.writeheader()
            writer.writerows({k:("'"+v if isinstance(v,str) and v.startswith(("=","+","-","@","\t","\r")) else v) for k,v in row.items()} for row in candidates[-1])
    paths={ext: str((report_dir / f"report.{ext}").resolve()) for ext in ("md", "json", "html")}
    if candidates:
        paths["csv"]=str((report_dir/"traffic_boost_candidates.csv").resolve())
    return {"report_id": report_id, "human_approved": False, "validation": "引用存在、快照/日期/指标配置一致；数字从工具结果渲染。定性判断需人工审阅。",
            "paths": paths}
