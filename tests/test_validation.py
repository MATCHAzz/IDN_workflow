import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from liveops import knowledge
from liveops.ops_mock import generate
from liveops.store import Store, ToolError
from liveops.tools import ToolRegistry
from liveops.validation import validate_range, validate_scope

ROOT = Path(__file__).resolve().parent.parent


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_dir = tempfile.TemporaryDirectory()
        cls.source = Path(cls.source_dir.name)
        generate(cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.source_dir.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / "data"
        self.data.mkdir()
        shutil.copyfile(self.source / "liveops.sqlite", self.data / "liveops.sqlite")
        self.tools = ToolRegistry(self.data, self.root / "outputs")

    def test_date_and_cohort_validation_reject_invalid_inputs(self):
        store = Store(self.data / "liveops.sqlite")
        self.addCleanup(store.close)
        meta = store.metadata()
        cases = [("2026-9-01", "2026-09-02"), ("2026-09-02", "2026-09-01"),
                 ("2026-08-31", "2026-09-02"), ("2026-09-01", "2026-10-17")]
        for start, end in cases:
            with self.subTest(start=start), self.assertRaises(ToolError):
                validate_range(start, end, meta)
        for kwargs in ({"tier": "unknown"}, {"campaign_id": "x' OR 1=1--"},
                       {"streamer_id": True}, {"streamer_id": 999999}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ToolError):
                validate_scope(store, **kwargs)

    def test_source_integrity_failures_block_fixed_query(self):
        mutations = [
            "UPDATE transactions SET amount_idr=amount_idr+1 WHERE transaction_id=1",
            "UPDATE view_sessions SET user_id=999999 WHERE session_id=1",
            "DELETE FROM view_sessions WHERE date='2026-10-17'",
            "DELETE FROM traffic_boost_daily WHERE date='2026-10-17' AND streamer_id=1",
            "UPDATE streamer_daily SET live_seconds=-1 WHERE date='2026-10-17' AND streamer_id=1",
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                shutil.copyfile(self.source / "liveops.sqlite", self.data / "liveops.sqlite")
                with closing(sqlite3.connect(self.data / "liveops.sqlite")) as con:
                    con.execute(mutation)
                    con.commit()
                result = self.tools.call("query_gift_total", {
                    "start_date": "2026-10-11", "end_date": "2026-10-17"}, "invalid-source")
                self.assertEqual(result["error"]["code"], "QUALITY_FAILED")

    def test_config_change_invalidates_existing_plan_and_changes_sql_bindings(self):
        old = self.tools.call("prepare_analysis", {
            "workflow": "weekly_report", "report_date": "2026-10-17"}, "config")
        cfg = json.loads(knowledge.CONFIG_PATH.read_text())
        cfg["effective_live_day"]["min_live_seconds"] = 999999
        path = self.root / "config.json"
        path.write_text(json.dumps(cfg))
        with patch.object(knowledge, "CONFIG_PATH", path):
            stale = self.tools.call("execute_readonly_sql", {
                "plan_evidence_id": old["evidence_id"], "knowledge_id": old["knowledge_id"],
                "sql": "SELECT SUM(amount_idr) AS total FROM gift_events"}, "config")
            self.assertEqual(stale["error"]["code"], "KNOWLEDGE_MISMATCH")
            fresh = self.tools.call("prepare_analysis", {
                "workflow": "weekly_report", "report_date": "2026-10-17"}, "new-config")
            result = self.tools.call("execute_readonly_sql", {
                "plan_evidence_id": fresh["evidence_id"], "knowledge_id": fresh["knowledge_id"],
                "sql": (ROOT / "knowledge/sql_examples/period_metrics.sql").read_text(),
                "result_kind": "metrics"}, "new-config")
            self.assertEqual(result["status"], "ok", result.get("error"))
            self.assertEqual(result["result"]["rows"][0]["effective_live_days"], 0)
            self.assertEqual(result["result"]["bound_parameters"]["min_live_seconds"], 999999)

    def test_invalid_config_cannot_be_used(self):
        cfg = json.loads(knowledge.CONFIG_PATH.read_text())
        cfg["monitoring"]["relative_drop_threshold"] = False
        path = self.root / "invalid-config.json"
        path.write_text(json.dumps(cfg))
        with patch.object(knowledge, "CONFIG_PATH", path), self.assertRaises(ToolError):
            knowledge.contract()

    def test_store_rejects_writes_and_unapproved_tables(self):
        before = (self.data / "liveops.sqlite").read_bytes()
        store = Store(self.data / "liveops.sqlite")
        self.addCleanup(store.close)
        for sql in ("DELETE FROM transactions", "SELECT * FROM sqlite_master"):
            with self.subTest(sql=sql), self.assertRaises(sqlite3.DatabaseError):
                store.query("denied", sql)
        self.assertEqual((self.data / "liveops.sqlite").read_bytes(), before)

    def test_generator_preserves_existing_snapshot(self):
        target = self.root / "generated"
        generate(target)
        before = (target / "liveops.sqlite").read_bytes()
        with self.assertRaises(FileExistsError):
            generate(target)
        self.assertEqual((target / "liveops.sqlite").read_bytes(), before)

    def test_cli_catalog_and_fixed_query(self):
        base = [sys.executable, "-m", "liveops", "--data-dir", str(self.data),
                "--output-dir", str(self.root / "cli-output")]
        catalog = subprocess.run(base + ["tools"], cwd=ROOT, text=True, capture_output=True, check=True)
        names = {item["name"] for item in json.loads(catalog.stdout)["tools"]}
        self.assertIn("execute_readonly_sql", names)
        self.assertIn("query_gift_total", names)
        self.assertNotIn("query_kpis", names)
        args = self.root / "query.json"
        args.write_text(json.dumps({"start_date": "2026-10-11", "end_date": "2026-10-17"}))
        query = subprocess.run(base + ["call", "query_gift_total", "--args-file", str(args)],
                               cwd=ROOT, text=True, capture_output=True, check=True)
        result = json.loads(query.stdout)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(Path(result["artifact_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
