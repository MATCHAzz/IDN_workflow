"""Build local navigation for completed SQL reports."""
import html
import json
from pathlib import Path

TASKS={"weekly_report":"周报更新","campaign_review":"活动复盘","traffic_boost_update":"主播流量助推更新"}


def workspace_index(output_dir):
    """Local report navigation; no network or application writes."""
    output_dir=Path(output_dir).resolve()
    latest={}
    for path in sorted((output_dir/"runs").glob("*/workflow_state.json"),key=lambda p:p.stat().st_mtime,reverse=True):
        try:
            item=json.loads(path.read_text())
            kind=item["request"]["workflow"]
            if item["status"]=="completed" and kind in TASKS and kind not in latest:
                report_path=Path(item["report_paths"]["html"])
                if report_path.is_file():
                    latest[kind]=report_path.resolve()
        except (OSError,ValueError,KeyError):
            continue
    directory=output_dir/"operations"
    directory.mkdir(exist_ok=True)
    links=[]
    source=""
    for kind,label in TASKS.items():
        if kind not in latest:
            continue
        relative="../"+latest[kind].relative_to(output_dir).as_posix()
        source=source or relative
        links.append(f'<a href="{html.escape(relative,quote=True)}" target="report">{label}</a>')
    content="""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>运营自动化 · 周报与任务复盘</title><style>
body{margin:0;background:#edf2f7;color:#162d42;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}header{padding:24px 32px;background:#112d48;color:white}h1{margin:0 0 10px;font-size:26px}p{margin:6px 0;line-height:1.7;color:#c8dbe9}nav{display:flex;gap:12px;padding:16px 32px;flex-wrap:wrap}a{background:#fff;color:#007f83;padding:10px 18px;border-radius:10px;text-decoration:none;border:1px solid #ccdce6}a:hover,a:focus{background:#d9efef}iframe{display:block;border:0;width:100%;height:78vh;min-height:650px;background:#edf2f7}.notice{color:#52677b;padding:0 32px;font-size:13px}</style>
<header><h1>运营自动化工作台</h1><p>周报更新 → 活动复盘 → 主播流量助推更新</p><p>统一监控：打赏金额 · 看播时长 · 有效直播天数 · 直播时长 · 观看观众数</p></header><nav>__LINKS__</nav><p class="notice">当前为合成数据、本地看板与待推送草稿。内部数据系统、真实定时推送和流量下发尚未配置。</p><iframe name="report" title="任务分析看板" src="__SOURCE__"></iframe></html>"""
    path=directory/"index.html"
    path.write_text(content.replace("__LINKS__","".join(links)).replace("__SOURCE__",html.escape(source,quote=True)))
    return str(path.resolve())

