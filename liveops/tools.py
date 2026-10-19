"""Tool registry for the native Agent, shared with the CLI."""
import inspect
import json
import re
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from . import METRIC_VERSION, RULE_VERSION, TIMEZONE
from .knowledge import contract
from .sql_tools import SQLToolsMixin
from .store import Store, ToolError
from .validation import quality

ROOT = Path(__file__).resolve().parent.parent


class ToolRegistry(SQLToolsMixin):
    """Knowledge and Agent SQL tools, plus one fixed business query."""
    def __init__(self,data_dir=None,output_dir=None):
        self.data_dir = Path(data_dir) if data_dir else ROOT / "data" / "operations-v2"
        self.output_dir = Path(output_dir) if output_dir else ROOT / "outputs"
        definitions={
            "get_data_profile":"data-quality-check","read_business_knowledge":"business-kpi-analysis",
            "search_business_knowledge":"business-kpi-analysis",
            "get_metric_dictionary":"business-kpi-analysis","check_data_quality":"data-quality-check",
            "prepare_analysis":"weekly-report-update","execute_readonly_sql":"business-kpi-analysis",
            "assemble_analysis":"business-report-writing","export_report":"business-report-writing",
            "prepare_delivery":"business-report-writing","query_gift_total":"business-kpi-analysis",
        }
        self.entries={name:(skill,getattr(self,name)) for name,skill in definitions.items()}

    def describe(self):
        return {"architecture":"Skills + file knowledge + Agent-authored SQL + read-only execution",
                "tools":[{"name":name,"skill":skill,"arguments":str(inspect.signature(fn)).replace("store, meta, ","").replace("store,meta,","").replace("store, meta","").replace("store,meta","")}
                         for name,(skill,fn) in self.entries.items()],
                "fixed_query":"query_gift_total / liveops/simple_query.py", "knowledge_directory":str(ROOT/"knowledge"),
                "note":"run-plan只重放Agent已写好的SQL计划，不替代Agent理解自然语言。"}

    def call(self, name, arguments=None, run_id=None):
        run_id = run_id or ("run-" + uuid.uuid4().hex[:12])
        if not isinstance(run_id, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", run_id):
            raise ToolError("INVALID_RUN_ID", "run_id 仅允许字母数字、下划线和连字符，最多64字符")
        run_dir = self.output_dir / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        # Reserve an immutable evidence slot; parallel tool calls cannot overwrite one another.
        sequence = 1
        while sequence <= 9999:
            eid = f"e{sequence:04d}"
            path = run_dir / f"{eid}.json"
            try:
                file = path.open("x", encoding="utf-8")
                break
            except FileExistsError:
                sequence += 1
        else:
            raise ToolError("RUN_LIMIT", "单次运行超过证据数量上限")
        started = time.perf_counter()
        envelope = {"run_id": run_id, "evidence_id": eid, "tool": name,
                    "arguments": arguments if arguments is not None else {},
                    "status": "error", "metric_version": METRIC_VERSION, "rule_version": RULE_VERSION,
                    "timezone": TIMEZONE, "synthetic": True,
                    "executed_at": datetime.now(timezone.utc).isoformat(), "warnings": [], "query_ids": []}
        store = None
        try:
            if name not in self.entries:
                raise ToolError("UNKNOWN_TOOL", "工具不在目录；动态查询请使用execute_readonly_sql，不支持任意shell或敏感明细读取")
            if not isinstance(envelope["arguments"], dict):
                raise ToolError("INVALID_ARGUMENTS", "arguments 必须为 JSON 对象")
            skill, fn = self.entries[name]
            envelope["skill"] = skill
            try:
                inspect.signature(fn).bind(None, None, **envelope["arguments"])
            except TypeError as exc:
                raise ToolError("INVALID_ARGUMENTS", str(exc)) from None
            store = Store(self.data_dir / "liveops.sqlite")
            meta = store.metadata()
            if meta.get("synthetic") != "true" or meta.get("timezone") != TIMEZONE or meta.get("generator_version") != "operations-v2":
                raise ToolError("INVALID_SNAPSHOT", "本工具只接受 Asia/Jakarta 的operations-v2合成快照")
            envelope.update({"snapshot_id": meta["snapshot_id"], "data_as_of": meta["end_date"] + "T23:59:59+07:00"})
            envelope["metric_version"] = meta.get("metric_version", METRIC_VERSION)
            envelope["rule_version"] = meta.get("rule_version", RULE_VERSION)
            self._run_dir = run_dir
            active=contract()
            envelope.update({"knowledge_id":active["knowledge_id"],"metric_version":active["metric_version"],"config_id":active["config_id"],"rule_version":RULE_VERSION})
            result = fn(store, meta, **envelope["arguments"])
            envelope.update({"status": "ok", "result": result, "warnings": result.get("warnings", [])})
        except ToolError as exc:
            envelope["error"] = {"code": exc.code, "message": str(exc)}
        except (sqlite3.Error, KeyError) as exc:
            envelope["error"] = {"code": "DATA_ERROR", "message": "快照结构/查询异常，停止分析：" + str(exc)}
        except (ValueError, TypeError) as exc:
            envelope["error"] = {"code": "INVALID_ARGUMENTS", "message": str(exc)}
        except OSError as exc:
            envelope["error"] = {"code": "FILE_ERROR", "message": str(exc)}
        finally:
            if store:
                envelope["queries"] = store.queries
                envelope["query_ids"] = list(dict.fromkeys(q["query_id"] for q in store.queries))
                store.close()
            envelope["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 3)
            envelope["artifact_path"] = str(path.resolve())
            json.dump(envelope, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write("\n")
            file.close()
        return envelope

    def get_data_profile(self, store, meta):
        counts = {}
        for table in ("users", "streamers", "view_sessions", "payment_attempts", "transactions"):
            counts[table] = store.query("profile_" + table, f"SELECT COUNT(*) n FROM {table}")[0]["n"]
        result = {"date_range": [meta["start_date"], meta["end_date"]], "row_counts": counts,
                "snapshot_id": meta["snapshot_id"], "timezone": TIMEZONE, "synthetic": True,
                "warnings": ["仅合成数据，内部数据系统连接尚未配置。"]}
        if meta.get("generator_version") == "operations-v2":
            for table in ("streamer_daily", "traffic_boost_daily"):
                counts[table] = store.query("profile_"+table, f"SELECT COUNT(*) n FROM {table}")[0]["n"]
            result["campaigns"] = store.query("profile_campaigns", "SELECT * FROM campaigns ORDER BY campaign_id")
            result["primary_metrics"] = list(contract()["metrics"])
        return result

    def check_data_quality(self, store, meta, start_date, end_date):
        return quality(store, start_date, end_date, meta)
