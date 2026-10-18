"""Trusted infrastructure SQL connection; Agent SQL uses GeneratedSQLStore plus AST checks."""
import hashlib
import json
import sqlite3
import time
from pathlib import Path


class ToolError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class Store:
    def __init__(self, path: Path):
        if not path.is_file():
            raise ToolError("DATA_NOT_INITIALIZED", "请先执行 python3 -m liveops init")
        self.con = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA query_only=ON")
        self.queries = []
        self.deadline = 0
        self.con.set_progress_handler(lambda: int(time.monotonic() > self.deadline), 1000)
        self.con.set_authorizer(self._authorize)

    @staticmethod
    def _authorize(action, arg1, arg2, database, trigger):
        if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ:
            return sqlite3.SQLITE_OK if arg1 in {
                "users", "streamers", "view_sessions", "payment_attempts", "transactions", "metadata",
                "streamer_daily", "campaigns", "campaign_streamers", "traffic_boost_daily"
            } else sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_FUNCTION:
            return sqlite3.SQLITE_OK if (arg2 or "").lower() in {
                "sum", "count", "min", "max", "coalesce", "round", "abs", "typeof", "length"
            } else sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_DENY

    def query(self, label, sql, params=None):
        params = params or {}
        self.deadline = time.monotonic() + 5
        qid = "q-" + hashlib.sha256((label + sql + json.dumps(params, sort_keys=True)).encode()).hexdigest()[:16]
        started = time.perf_counter()
        rows = self.con.execute(sql, params).fetchmany(501)
        if len(rows) > 500:
            raise ToolError("ROW_LIMIT", "查询超过 500 行聚合结果上限")
        self.queries.append({"query_id": qid, "template": label, "sql": sql, "parameters": params,
                             "elapsed_ms": round((time.perf_counter() - started) * 1000, 3)})
        return [dict(row) for row in rows]

    def metadata(self):
        return {row["key"]: row["value"] for row in self.query("metadata", "SELECT key,value FROM metadata")}

    def close(self):
        self.con.close()
