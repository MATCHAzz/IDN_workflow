"""Load file-based business knowledge; execution logic lives elsewhere."""
import hashlib
import json
from pathlib import Path

from .store import ToolError

ROOT=Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR=ROOT/"knowledge"
CONFIG_PATH=ROOT/"config/operations_metrics.json"


def config():
    value=json.loads(CONFIG_PATH.read_text())
    if value.get("timezone")!="Asia/Jakarta":
        raise ToolError("INVALID_CONFIG","指标时区必须为Asia/Jakarta")
    for key in ("min_live_seconds","min_watch_seconds"):
        v=value["effective_live_day"][key]
        if not isinstance(v,int) or isinstance(v,bool) or v<0:
            raise ToolError("INVALID_CONFIG","有效直播门槛必须为非负整数秒")
    threshold=value["monitoring"]["relative_drop_threshold"]
    if not isinstance(threshold,(int,float)) or isinstance(threshold,bool) or not 0<threshold<=1:
        raise ToolError("INVALID_CONFIG","下降阈值必须在(0,1]内")
    for section,key in (("monitoring","minimum_viewers_for_alert"),("traffic_boost","min_effective_days_7d"),("traffic_boost","min_viewer_uv_7d"),("traffic_boost","suggested_units_per_streamer")):
        v=value[section][key]
        if not isinstance(v,int) or isinstance(v,bool) or v<0:
            raise ToolError("INVALID_CONFIG",f"{section}.{key}必须为非负整数")
    return value


def contract():
    metrics=json.loads((KNOWLEDGE_DIR/"metrics.json").read_text())
    schema=json.loads((KNOWLEDGE_DIR/"schema.json").read_text())
    rules=config()
    digest=hashlib.sha256()
    for path in sorted(KNOWLEDGE_DIR.rglob("*")):
        if path.is_file() and path.suffix in {".json",".md",".sql"}:
            digest.update(path.relative_to(KNOWLEDGE_DIR).as_posix().encode())
            digest.update(path.read_bytes())
    digest.update(json.dumps(rules,sort_keys=True).encode())
    return {"metric_version":metrics["version"],"knowledge_id":digest.hexdigest(),
            "config_id":hashlib.sha256(json.dumps(rules,sort_keys=True).encode()).hexdigest()[:12],
            "timezone":metrics["timezone"],"metrics":metrics["metrics"],"invariants":metrics["invariants"],
            "schema":schema,"rules":rules}


def read(topic="metrics"):
    if topic not in {"metrics","weekly_report","campaign_review","traffic_boost_update","ad_hoc"}:
        raise ToolError("UNKNOWN_KNOWLEDGE_TOPIC","不支持的业务知识主题")
    value=contract()
    value.update({"topic":topic,"instructions":(KNOWLEDGE_DIR/"rules.md").read_text(),
                  "example_paths":[str(p.resolve()) for p in sorted((KNOWLEDGE_DIR/"sql_examples").glob("*.sql"))],
                  "note":"参考SQL由Agent主动读取并按任务编写；工具不会自动从问题生成SQL。"})
    return value
