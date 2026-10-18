import json
import shutil
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from liveops import knowledge
from liveops.ops_mock import generate
from liveops.plan_runner import run_plan
from liveops.store import ToolError
from liveops.tools import ToolRegistry

ROOT=Path(__file__).resolve().parent.parent


class AgentSQLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=tempfile.TemporaryDirectory()
        cls.source=Path(cls.base.name)/"source"
        generate(cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.base.cleanup()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.data=self.root/"data"
        self.data.mkdir()
        shutil.copyfile(self.source/"liveops.sqlite",self.data/"liveops.sqlite")
        self.out=self.root/"outputs"
        self.tools=ToolRegistry(self.data,self.out)
        self.plan=self.ok("prepare_analysis",workflow="weekly_report",report_date="2026-10-17")

    def call(self,name,**args):
        return self.tools.call(name,args,"agent-test")

    def ok(self,name,**args):
        result=self.call(name,**args)
        self.assertEqual(result["status"],"ok",result.get("error"))
        return result

    def query(self,sql,kind="table",window="current",**kwargs):
        return self.call("execute_readonly_sql",plan_evidence_id=self.plan["evidence_id"],knowledge_id=self.plan["knowledge_id"],sql=sql,result_kind=kind,window=window,**kwargs)

    def example(self,name,kind,window="current",**kwargs):
        response=self.query((ROOT/"knowledge/sql_examples"/name).read_text(),kind,window,**kwargs)
        self.assertEqual(response["status"],"ok",response.get("error"))
        return response

    def independent_metrics(self,start,end,tier=None,streamer_id=None):
        """Scalar source queries independent of Agent SQL/CTE construction."""
        conditions=[]
        parameters={"start":start,"end":end}
        if tier is not None:
            conditions.append("s.tier=:tier")
            parameters["tier"]=tier
        if streamer_id is not None:
            conditions.append("s.streamer_id=:sid")
            parameters["sid"]=streamer_id
        scope=" AND "+" AND ".join(conditions) if conditions else ""
        cfg=knowledge.contract()["rules"]["effective_live_day"]
        parameters.update(min_live=cfg["min_live_seconds"],min_watch=cfg["min_watch_seconds"])
        with closing(sqlite3.connect(self.data/"liveops.sqlite")) as con:
            gift=con.execute("SELECT COALESCE(SUM(t.amount_idr),0) FROM transactions t JOIN streamers s USING(streamer_id) WHERE t.date BETWEEN :start AND :end"+scope,parameters).fetchone()[0]
            watch,uv=con.execute("SELECT COALESCE(SUM(v.duration_seconds),0)/3600.0,COUNT(DISTINCT v.user_id) FROM view_sessions v JOIN streamers s USING(streamer_id) WHERE v.date BETWEEN :start AND :end"+scope,parameters).fetchone()
            live,effective=con.execute("""SELECT COALESCE(SUM(b.live_seconds),0)/3600.0,
                COALESCE(SUM(CASE WHEN b.live_seconds>0 AND b.live_seconds>=:min_live AND
                (SELECT COALESCE(SUM(v.duration_seconds),0) FROM view_sessions v WHERE v.date=b.date AND v.streamer_id=b.streamer_id)>=:min_watch THEN 1 ELSE 0 END),0)
                FROM streamer_daily b JOIN streamers s USING(streamer_id) WHERE b.date BETWEEN :start AND :end"""+scope,parameters).fetchone()
        return {"gift_amount_idr":gift,"watch_duration_hours":watch,"viewer_uv":uv,"live_duration_hours":live,"effective_live_days":effective}

    def test_dynamic_five_metrics_match_independent_sql(self):
        row=self.example("period_metrics.sql","metrics")["result"]["rows"][0]
        with closing(sqlite3.connect(self.data/"liveops.sqlite")) as con:
            gift=con.execute("SELECT SUM(amount_idr) FROM transactions WHERE date BETWEEN '2026-10-11' AND '2026-10-17'").fetchone()[0]
            watch,uv=con.execute("SELECT SUM(duration_seconds)/3600.0,COUNT(DISTINCT user_id) FROM view_sessions WHERE date BETWEEN '2026-10-11' AND '2026-10-17'").fetchone()
            live=con.execute("SELECT SUM(live_seconds)/3600.0 FROM streamer_daily WHERE date BETWEEN '2026-10-11' AND '2026-10-17'").fetchone()[0]
        self.assertEqual(row["gift_amount_idr"],gift)
        self.assertAlmostEqual(row["watch_duration_hours"],watch)
        self.assertEqual(row["viewer_uv"],uv)
        self.assertAlmostEqual(row["live_duration_hours"],live)
        reference=self.independent_metrics("2026-10-11","2026-10-17")
        self.assertEqual(row["effective_live_days"],reference["effective_live_days"])

    def test_comparison_matches_independent_metrics_and_thresholds(self):
        current=self.example("period_metrics.sql","metrics")
        compared=self.example("period_comparison.sql","comparison","comparison")
        rules=knowledge.contract()["rules"]["monitoring"]
        actual={(r["dimension"],r["metric"]):r for r in compared["result"]["rows"]}
        self.assertEqual(len(actual),20)
        for dimension in ("all","head","mid","tail"):
            tier=None if dimension=="all" else dimension
            now=self.independent_metrics("2026-10-11","2026-10-17",tier)
            prior=self.independent_metrics("2026-10-04","2026-10-10",tier)
            for key,value in now.items():
                row=actual[dimension,key]
                self.assertAlmostEqual(row["current"],value)
                self.assertAlmostEqual(row["baseline"],prior[key])
                change=(value-prior[key])/prior[key] if prior[key] else None
                sample=min(now["viewer_uv"],prior["viewer_uv"])>=rules["minimum_viewers_for_alert"]
                alert=change<=-rules["relative_drop_threshold"] if change is not None and sample else None
                self.assertEqual(row["is_anomaly"],alert)
        self.ok("assemble_analysis",plan_evidence_id=self.plan["evidence_id"],query_evidence_ids=[current["evidence_id"],compared["evidence_id"]])

    def test_agent_can_change_query_and_scope(self):
        sql="SELECT s.tier,COUNT(DISTINCT w.viewer_id) AS viewers FROM watch_events w JOIN streamer_profiles s ON w.streamer_id=s.streamer_id GROUP BY s.tier"
        result=self.query(sql,filters={"streamer_tier":"tail"})
        self.assertEqual(result["status"],"ok",result.get("error"))
        self.assertEqual([r["tier"] for r in result["result"]["rows"]],["tail"])
        with closing(sqlite3.connect(self.data/"liveops.sqlite")) as con:
            expected=con.execute("SELECT COUNT(DISTINCT v.user_id) FROM view_sessions v JOIN streamers s ON v.streamer_id=s.streamer_id WHERE s.tier='tail' AND v.date BETWEEN '2026-10-11' AND '2026-10-17'").fetchone()[0]
        self.assertEqual(result["result"]["rows"][0]["viewers"],expected)

    def test_source_date_scoping_is_enforced_without_where(self):
        result=self.query("SELECT MIN(date) AS first_day,MAX(date) AS last_day FROM gift_events")
        self.assertEqual(result["status"],"ok",result.get("error"))
        self.assertEqual(result["result"]["rows"],[{"first_day":"2026-10-11","last_day":"2026-10-17"}])
        denied=self.query("SELECT SUM(amount_idr) AS total FROM gift_events",parameters={"start_date":"2000-01-01"})
        self.assertEqual(denied["error"]["code"],"RESERVED_PARAMETER")

    def test_campaign_scope_is_frozen(self):
        self.plan=self.ok("prepare_analysis",workflow="campaign_review",campaign_id="idn-oct-mission")
        result=self.example("period_metrics.sql","metrics")["result"]["rows"][0]
        with closing(sqlite3.connect(self.data/"liveops.sqlite")) as con:
            expected=con.execute("SELECT SUM(amount_idr) FROM transactions WHERE date BETWEEN '2026-10-08' AND '2026-10-14' AND streamer_id IN (SELECT streamer_id FROM campaign_streamers WHERE campaign_id='idn-oct-mission')").fetchone()[0]
        self.assertEqual(result["gift_amount_idr"],expected)
        denied=self.query("SELECT SUM(amount_idr) AS total FROM gift_events",filters={"campaign_id":"other"})
        self.assertEqual(denied["error"]["code"],"SCOPE_EXPANSION_DENIED")

    def test_fixed_query_agrees_with_dynamic_query(self):
        fixed=self.ok("query_gift_total",start_date="2026-10-11",end_date="2026-10-17")
        generated=self.query("SELECT COALESCE(SUM(amount_idr),0) AS gift_amount_idr FROM gift_events")
        self.assertEqual(fixed["result"]["rows"],generated["result"]["rows"])
        self.assertNotIn("update_weekly_report",{r["name"] for r in self.tools.describe()["tools"]})

    def test_ad_hoc_question_has_explicit_custom_dates(self):
        self.plan=self.ok("prepare_analysis",workflow="ad_hoc",start_date="2026-09-10",end_date="2026-09-12",streamer_tier="mid")
        response=self.query("SELECT MIN(date) AS first_day,MAX(date) AS last_day,COUNT(DISTINCT viewer_id) AS viewers FROM watch_events")
        self.assertEqual(response["status"],"ok",response.get("error"))
        self.assertEqual(response["result"]["rows"][0]["first_day"],"2026-09-10")
        self.assertEqual(response["result"]["rows"][0]["last_day"],"2026-09-12")
        self.assertEqual(response["result"]["filters"],{"streamer_tier":"mid"})

    def test_mutation_and_unauthorized_sources_are_rejected(self):
        before=(self.data/"liveops.sqlite").read_bytes()
        cases=["DROP TABLE users","SELECT SUM(amount_idr) FROM gift_events; DELETE FROM transactions",
               "PRAGMA table_info(users)","ATTACH DATABASE '/tmp/x.sqlite' AS x",
               "SELECT COUNT(*) FROM users","SELECT COUNT(*) FROM main.transactions",
               "SELECT COUNT(*) FROM sqlite_master","WITH watch_events AS (SELECT 1) SELECT COUNT(*) FROM watch_events",
               "WITH RECURSIVE x(n) AS (SELECT 1 UNION ALL SELECT n+1 FROM x) SELECT n FROM x",
               "SELECT load_extension('/tmp/x') FROM gift_events"]
        for sql in cases:
            with self.subTest(sql=sql):
                self.assertEqual(self.query(sql)["status"],"error")
        self.assertEqual((self.data/"liveops.sqlite").read_bytes(),before)

    def test_user_detail_and_raw_fact_rows_are_rejected(self):
        cases=["SELECT viewer_id FROM watch_events","SELECT MAX(viewer_id) AS viewer_uv FROM watch_events",
               "SELECT COUNT(DISTINCT viewer_id) AS n FROM watch_events WHERE viewer_id=1",
               "SELECT viewer_id,COUNT(*) AS n FROM watch_events GROUP BY viewer_id",
               "WITH x AS (SELECT viewer_id AS v FROM watch_events) SELECT COUNT(DISTINCT v) FROM x",
               "SELECT duration_seconds FROM watch_events","SELECT amount_idr FROM gift_events",
               "SELECT * FROM streamer_profiles"]
        for sql in cases:
            with self.subTest(sql=sql):
                self.assertEqual(self.query(sql)["status"],"error")

    def test_direct_multi_fact_join_is_rejected(self):
        result=self.query("SELECT SUM(g.amount_idr) AS total FROM gift_events g JOIN watch_events w ON g.streamer_id=w.streamer_id")
        self.assertEqual(result["error"]["code"],"MULTI_FACT_JOIN")

    def test_excessive_results_are_rejected(self):
        result=self.query("SELECT date,streamer_id,SUM(amount_idr) AS gifts FROM gift_events GROUP BY date,streamer_id","table","comparison")
        self.assertEqual(result["error"]["code"],"ROW_LIMIT")

    def test_boost_sql_matches_sources_and_requires_full_cohort(self):
        self.plan=self.ok("prepare_analysis",workflow="traffic_boost_update",report_date="2026-10-17")
        result=self.example("boost_candidates.sql","boost")["result"]["rows"]
        rules=knowledge.contract()["rules"]["traffic_boost"]
        with closing(sqlite3.connect(self.data/"liveops.sqlite")) as con:
            previous=dict(con.execute("SELECT streamer_id,allocated_units FROM traffic_boost_daily WHERE date='2026-10-16'"))
        self.assertEqual({row["streamer_id"] for row in result},set(previous))
        for row in result:
            expected=self.independent_metrics("2026-10-11","2026-10-17",streamer_id=row["streamer_id"])
            for key,value in expected.items():
                self.assertAlmostEqual(row[key],value)
            eligible=expected["effective_live_days"]>=rules["min_effective_days_7d"] and expected["viewer_uv"]>=rules["min_viewer_uv_7d"]
            suggested=rules["suggested_units_per_streamer"] if eligible else 0
            old=previous[row["streamer_id"]]
            self.assertEqual(row["eligible"],eligible)
            self.assertEqual(row["suggested_units"],suggested)
            self.assertEqual(row["previous_units"],old)
            self.assertEqual(row["delta_units"],suggested-old)
            self.assertEqual(row["action"],"increase" if suggested>old else "decrease" if suggested<old else "keep")
        sql=(ROOT/"knowledge/sql_examples/boost_candidates.sql").read_text()+" LIMIT 1"
        response=self.query(sql,"boost")
        self.assertEqual(response["error"]["code"],"INCOMPLETE_BOOST_LIST")

    def test_knowledge_changes_invalidate_plan_and_report(self):
        metric=self.example("period_metrics.sql","metrics")
        temporary=self.root/"knowledge"
        shutil.copytree(ROOT/"knowledge",temporary)
        with (temporary/"rules.md").open("a") as file:
            file.write("\n更新的业务说明\n")
        with patch.object(knowledge,"KNOWLEDGE_DIR",temporary):
            result=self.query("SELECT SUM(amount_idr) AS total FROM gift_events")
            self.assertEqual(result["error"]["code"],"KNOWLEDGE_MISMATCH")
            result=self.call("export_report",date="2026-10-17",evidence_ids=[metric["evidence_id"]])
            self.assertEqual(result["error"]["code"],"KNOWLEDGE_MISMATCH")

    def test_quality_failure_blocks_dynamic_query(self):
        with closing(sqlite3.connect(self.data/"liveops.sqlite")) as con:
            con.execute("DELETE FROM streamer_daily WHERE date='2026-10-17' AND streamer_id=1")
            con.commit()
        result=self.query("SELECT SUM(amount_idr) AS total FROM gift_events")
        self.assertEqual(result["error"]["code"],"QUALITY_FAILED")

    def test_assembly_reconciles_separate_sql_results(self):
        current=self.example("period_metrics.sql","metrics")
        sql=(ROOT/"knowledge/sql_examples/period_comparison.sql").read_text()
        comparison=self.query(sql,"comparison","comparison")
        path=Path(current["artifact_path"])
        modified=json.loads(path.read_text())
        modified["result"]["rows"][0]["gift_amount_idr"]+=1
        path.write_text(json.dumps(modified))
        response=self.call("assemble_analysis",plan_evidence_id=self.plan["evidence_id"],query_evidence_ids=[current["evidence_id"],comparison["evidence_id"]])
        self.assertEqual(response["error"]["code"],"RESULT_RECONCILIATION")

    def test_run_plan_exports_sql_evidence_and_replays_idempotently(self):
        plan=ROOT/"examples/sql_plans/weekly_report.json"
        first=run_plan(plan,"replay",self.data,self.out)
        self.assertEqual(first["status"],"completed")
        report=json.loads(Path(first["report_paths"]["json"]).read_text())
        analysis=report["evidence"][0]["result"]
        self.assertEqual(analysis["analysis_mode"],"agent_generated_sql")
        self.assertTrue(any(e["result"]["filters"].get("streamer_tier")=="tail" for e in analysis["source_queries"]))
        for eid in analysis["source_evidence_ids"]:
            self.assertTrue((Path(first["report_paths"]["json"]).parent/(eid+".json")).is_file())
        self.assertEqual(json.loads(Path(first["delivery_draft"]).read_text())["status"],"draft_not_sent")
        count=len(list((self.out/"runs/replay").glob("e*.json")))
        replay=run_plan(plan,"replay",self.data,self.out)
        self.assertTrue(replay["idempotent_replay"])
        self.assertEqual(count,len(list((self.out/"runs/replay").glob("e*.json"))))

    def test_campaign_and_boost_plans_export(self):
        for name in ("campaign_review","traffic_boost_update"):
            result=run_plan(ROOT/f"examples/sql_plans/{name}.json",name,self.data,self.out)
            self.assertEqual(result["status"],"completed")
            if name=="traffic_boost_update":
                self.assertTrue(Path(result["report_paths"]["csv"]).is_file())

    def test_plan_cannot_override_executor_context(self):
        plan={"workflow":"weekly_report","report_date":"2026-10-17","queries":[{"sql":"SELECT SUM(amount_idr) FROM gift_events","plan_evidence_id":"e9999"}]}
        path=self.root/"bad.json"
        path.write_text(json.dumps(plan))
        with self.assertRaises(ToolError):
            run_plan(path,"bad",self.data,self.out)


if __name__=="__main__":
    unittest.main()
