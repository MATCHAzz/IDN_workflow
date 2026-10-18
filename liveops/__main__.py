import argparse
import json
import sys
from pathlib import Path

from .ops_mock import generate
from .store import ToolError
from .tools import ROOT, ToolRegistry


def main():
    parser = argparse.ArgumentParser(description="LiveOps 白名单 Python 工具；自然语言入口是本项目的 Agent 聊天")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "operations-v2")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="生成固定随机种子的 SQLite / CSV，已有快照不覆盖")
    sub.add_parser("tools", help="列出允许调用的工具及参数")
    call = sub.add_parser("call", help="执行一个工具，输出 JSON 并保存证据")
    call.add_argument("tool")
    source = call.add_mutually_exclusive_group()
    source.add_argument("--args", default=None, help="JSON 对象")
    source.add_argument("--args-file", type=Path, help="JSON 文件；避免复杂 shell 转义")
    call.add_argument("--run-id")
    replay=sub.add_parser("run-plan",help="执行Agent已编写的SQL计划，生成看板/清单和待推送包")
    replay.add_argument("--plan-file",required=True,type=Path)
    replay.add_argument("--run-id")
    args = parser.parse_args()
    try:
        registry = ToolRegistry(args.data_dir, args.output_dir)
        if args.command == "init":
            result = {"status": "ok", "manifest": generate(args.data_dir)}
        elif args.command == "tools":
            result = registry.describe()
        elif args.command == "run-plan":
            from .plan_runner import run_plan
            result=run_plan(args.plan_file,args.run_id,args.data_dir,args.output_dir)
        else:
            payload = args.args_file.read_text(encoding="utf-8") if args.args_file else (args.args or "{}")
            result = registry.call(args.tool, json.loads(payload), args.run_id)
        # Full SQL remains in evidence file, keeping Agent context focused on aggregates.
        display = {k: v for k, v in result.items() if k != "queries"}
        print(json.dumps(display, ensure_ascii=False, indent=2, allow_nan=False))
        return 0 if result.get("status", "ok") in {"ok","completed"} else 1
    except (ToolError, ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "error", "error": {"code": getattr(exc, "code", "INPUT_ERROR"), "message": str(exc)}}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
