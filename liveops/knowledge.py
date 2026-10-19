"""Load file-based business knowledge; execution logic lives elsewhere."""
import hashlib
import json
import re
import unicodedata
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


def _source_path(source):
    """Resolve only maintained knowledge files and the existing config source."""
    name=source["path"]
    if name=="config/operations_metrics.json":
        return CONFIG_PATH.resolve()
    path=(KNOWLEDGE_DIR/name).resolve()
    if not path.is_relative_to(KNOWLEDGE_DIR.resolve()) or path.suffix not in {".json",".md",".sql"}:
        raise ToolError("INVALID_KNOWLEDGE_INDEX","知识引用必须在knowledge目录内")
    return path


def _content(source):
    path=_source_path(source)
    text=path.read_text(encoding="utf-8")
    if "pointer" in source:
        value=json.loads(text)
        pointer=source["pointer"]
        if not isinstance(pointer,str) or not pointer.startswith("/"):
            raise ToolError("INVALID_KNOWLEDGE_INDEX","JSON引用需使用以/开头的pointer")
        for part in pointer[1:].split("/"):
            key=part.replace("~1","/").replace("~0","~")
            value=value[int(key)] if isinstance(value,list) else value[key]
        return value
    if "heading" in source:
        lines=text.splitlines()
        positions=[i for i,line in enumerate(lines) if line=="## "+source["heading"]]
        if len(positions)!=1:
            raise ToolError("INVALID_KNOWLEDGE_INDEX","知识章节不存在或不唯一："+source["heading"])
        start=positions[0]
        end=next((i for i in range(start+1,len(lines)) if re.match(r"^#{1,2} ",lines[i])),len(lines))
        return "\n".join(lines[start:end]).strip()
    return json.loads(text) if path.suffix==".json" else text


def _directory():
    """Validate links before returning a catalog; never silently drop broken rules."""
    try:
        catalog=json.loads((KNOWLEDGE_DIR/"catalog.json").read_text())
        routes=json.loads((KNOWLEDGE_DIR/"routes.json").read_text())
        if any(not isinstance(value.get("version"),str) or not value["version"] for value in (catalog,routes)):
            raise ValueError("目录和映射需要版本名称")
        entries={}
        topics=routes["topics"]
        if not isinstance(topics,dict) or not topics or not isinstance(routes["common"],list) or not routes["common"]:
            raise ValueError("任务映射或共同必读条目缺失")
        for item in catalog["entries"]:
            if not isinstance(item["id"],str) or not item["id"] or item["id"] in entries:
                raise ValueError("知识ID为空或重复")
            if not isinstance(item["title"],str) or not item["title"] or item["dialect"]!="sqlite":
                raise ValueError("知识名称或方言无效")
            for field in ("aliases","tags","topics","sources","requires"):
                if not isinstance(item[field],list) or any(not isinstance(v,str) or not v for v in item[field]):
                    raise ValueError("知识目录字段需为字符串数组："+field)
            if not item["topics"] or set(item["topics"])-set(topics):
                raise ValueError("知识条目引用未知主题")
            if set(item["sources"])-set(json.loads((KNOWLEDGE_DIR/"schema.json").read_text())["sources"]):
                raise ValueError("知识条目引用未知逻辑源")
            source=item["source"]
            if not isinstance(source,dict) or set(source)-{"path","pointer","heading"} or not isinstance(source.get("path"),str) or "pointer" in source and "heading" in source:
                raise ValueError("知识来源需为文件及可选JSON指针/Markdown章节")
            _content(source)
            entries[item["id"]]=item
        for topic,route in topics.items():
            if not isinstance(route["description"],str) or not isinstance(route["entries"],list):
                raise ValueError("任务映射需description和entries")
            for eid in routes["common"]+route["entries"]:
                if eid not in entries or topic not in entries[eid]["topics"]:
                    raise ValueError("任务映射引用缺失或不适用的知识："+str(eid))
        def visit(eid,active,done):
            if eid not in entries:
                raise ValueError("知识依赖不存在："+str(eid))
            if eid in active:
                raise ValueError("知识依赖形成循环："+eid)
            if eid in done:
                return
            for dependency in entries[eid]["requires"]:
                visit(dependency,active|{eid},done)
            done.add(eid)
        done=set()
        for eid in entries:
            visit(eid,set(),done)
        return catalog,routes,entries
    except ToolError:
        raise
    except (OSError,ValueError,TypeError,KeyError,IndexError,AttributeError) as exc:
        raise ToolError("INVALID_KNOWLEDGE_INDEX","知识目录或映射无效："+str(exc)) from None


def _topic(topic,routes):
    if not isinstance(topic,str) or topic not in routes["topics"]:
        raise ToolError("UNKNOWN_KNOWLEDGE_TOPIC","不支持的业务知识主题")


def _strings(value,name):
    if not isinstance(value,list) or any(not isinstance(v,str) or not v.strip() for v in value):
        raise ToolError("INVALID_ARGUMENTS",name+"需为字符串数组，元素不能为空")
    return list(dict.fromkeys(value))


def _metadata(item):
    return {**item,"source":{**item["source"],"absolute_path":str(_source_path(item["source"]))}}


def _normalize(text):
    return unicodedata.normalize("NFKC",text).casefold().strip()


def search(query=None,topic=None,tags=None):
    """Deterministic alias/tag lookup; it does not interpret tasks or choose SQL."""
    catalog,routes,entries=_directory()
    if topic is not None:
        _topic(topic,routes)
    if query is not None and (not isinstance(query,str) or not query.strip() or len(query)>1000):
        raise ToolError("INVALID_ARGUMENTS","query需为1到1000字的字符串")
    tags=[] if tags is None else _strings(tags,"tags")
    required_tags={_normalize(t) for t in tags}
    hits=[]
    for item in entries.values():
        if topic is not None and topic not in item["topics"]:
            continue
        if not required_tags.issubset({_normalize(t) for t in item["tags"]}):
            continue
        terms=[item["id"],item["title"],*item["aliases"],*item["tags"],*item["sources"]]
        matched=[term for term in terms if query is not None and
                 (_normalize(term) in _normalize(query) or _normalize(query) in _normalize(term))]
        if query is not None and not matched:
            continue
        hits.append({**_metadata(item),"matched_terms":list(dict.fromkeys(matched))})
    active=contract()
    return {"knowledge_id":active["knowledge_id"],"catalog_version":catalog["version"],
            "routes_version":routes["version"],"query":query,"topic":topic,"tags":tags,
            "available_topics":routes["topics"],"entries":hits,"match_count":len(hits),
            "note":"按名称、别名、标签、逻辑源做确定性匹配；不理解语义、不执行SQL。无匹配时请查看完整目录或补充问题，不猜测指标。"}


def read(topic="metrics",entry_ids=None):
    catalog,routes,entries=_directory()
    _topic(topic,routes)
    requested=[] if entry_ids is None else _strings(entry_ids,"entry_ids")
    unknown=set(requested)-set(entries)
    if unknown:
        raise ToolError("UNKNOWN_KNOWLEDGE_ENTRY","知识条目不存在："+", ".join(sorted(unknown)))
    selected={}
    def include(eid,reason):
        if eid in selected:
            if reason not in selected[eid]:
                selected[eid].append(reason)
            return
        selected[eid]=[reason]
        for dependency in entries[eid]["requires"]:
            include(dependency,"dependency:"+eid)
    for eid in routes["common"]:
        include(eid,"common")
    for eid in routes["topics"][topic]["entries"]:
        include(eid,"topic:"+topic)
    for eid in requested:
        include(eid,"requested")
    loaded=[]
    for eid,reasons in selected.items():
        item=entries[eid]
        content=_content(item["source"])
        loaded.append({**_metadata(item),"selection_reasons":reasons,"content":content,
                       "source_sha256":hashlib.sha256(_source_path(item["source"]).read_bytes()).hexdigest()})
    value=contract()
    value.update({"topic":topic,"routing":{"description":routes["topics"][topic]["description"],
                  "catalog_version":catalog["version"],"routes_version":routes["version"],
                  "requested_entry_ids":requested,"selected_entry_ids":list(selected)},
                  "knowledge_entries":loaded,
                  "instructions":"\n\n".join(item["content"] for item in loaded if item["source"]["path"]=="rules.md"),
                  "example_paths":list(dict.fromkeys(item["source"]["absolute_path"] for item in loaded if item["source"]["path"].endswith(".sql"))),
                  "note":"共通知识始终加载；任务映射和指定条目会补齐依赖。所有主题共用全库knowledge_id。SQL仅供Agent参考改写，不自动选择或执行。"})
    return value
