"""Knowledge routing behavior, dependency loading and global version boundaries."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from liveops import knowledge
from liveops.store import ToolError


class KnowledgeRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/"knowledge"
        shutil.copytree(knowledge.KNOWLEDGE_DIR,self.directory)
        self.patcher=patch.object(knowledge,"KNOWLEDGE_DIR",self.directory)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def change(self,name,mutate):
        path=self.directory/name
        value=json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value,ensure_ascii=False))

    def test_workflows_receive_relevant_rules_and_sql_without_losing_shared_constraints(self):
        weekly=knowledge.read("weekly_report")
        campaign=knowledge.read("campaign_review")
        boost=knowledge.read("traffic_boost_update")
        for result in (weekly,campaign,boost):
            ids=result["routing"]["selected_entry_ids"]
            for eid in ("rule.common","rule.result_contract","metric.viewer_uv","metric.invariants","schema.logical_sources","config.operations"):
                self.assertIn(eid,ids)
            self.assertIn("viewer_id仅可COUNT(DISTINCT viewer_id)",result["instructions"])
            self.assertEqual(set(result["metrics"]),set(knowledge.contract()["metrics"]))
        self.assertIn("截至日往前7天",weekly["instructions"])
        self.assertNotIn("## 主播助推",weekly["instructions"])
        self.assertIn("冻结名单",campaign["instructions"])
        self.assertNotIn("## 周报",campaign["instructions"])
        self.assertEqual({Path(p).name for p in boost["example_paths"]},{"period_metrics.sql","boost_candidates.sql"})
        self.assertNotIn("boost_candidates.sql",{Path(p).name for p in weekly["example_paths"]})
        self.assertEqual(weekly["knowledge_id"],boost["knowledge_id"])

    def test_natural_language_alias_can_be_found_then_read_with_uv_constraints(self):
        found=knowledge.search("活动期间有多少独立观众",topic="campaign_review")
        hits={item["id"]:item for item in found["entries"]}
        self.assertIn("metric.viewer_uv",hits)
        self.assertIn("独立观众",hits["metric.viewer_uv"]["matched_terms"])
        self.assertNotIn("content",hits["metric.viewer_uv"])
        result=knowledge.read("campaign_review",["metric.viewer_uv"])
        items={item["id"]:item for item in result["knowledge_entries"]}
        self.assertEqual(items["metric.viewer_uv"]["content"]["aggregation"],"COUNT(DISTINCT viewer_id)")
        self.assertIn("不相加每日或分组UV",items["metric.viewer_uv"]["content"]["definition"])
        self.assertIn("metric.invariants",items)
        self.assertIn("requested",items["metric.viewer_uv"]["selection_reasons"])
        self.assertEqual(found["knowledge_id"],result["knowledge_id"])

    def test_tags_and_topic_scope_directory_and_unknown_queries_do_not_guess(self):
        hits=knowledge.search(tags=["SQL","助推"],topic="traffic_boost_update")["entries"]
        self.assertEqual([item["id"] for item in hits],["sql.boost_candidates"])
        self.assertEqual(knowledge.search(tags=["SQL","助推"],topic="weekly_report")["entries"],[])
        self.assertEqual(knowledge.search("火星退款净利润")["match_count"],0)
        self.assertTrue(knowledge.search()["entries"])

    def test_supplemental_reads_load_dependencies_and_preserve_global_version(self):
        before=knowledge.read("weekly_report")
        supplemental=knowledge.read("root_cause_drilldown",["sql.boost_candidates"])
        self.assertIn("rule.boost",supplemental["routing"]["selected_entry_ids"])
        items={item["id"]:item for item in supplemental["knowledge_entries"]}
        self.assertIn("dependency:sql.boost_candidates",items["rule.boost"]["selection_reasons"])
        self.assertEqual(before["knowledge_id"],supplemental["knowledge_id"])
        self.assertEqual(len(items),len(supplemental["knowledge_entries"]))

    def test_catalog_routes_and_unselected_content_all_change_global_version(self):
        initial=knowledge.read("weekly_report")["knowledge_id"]
        self.change("catalog.json",lambda value:value["entries"][0]["aliases"].append("新增别名"))
        catalog_version=knowledge.read("weekly_report")["knowledge_id"]
        self.assertNotEqual(initial,catalog_version)
        self.change("routes.json",lambda value:value["topics"]["ad_hoc"].update(description="更新目录说明"))
        route_version=knowledge.read("weekly_report")["knowledge_id"]
        self.assertNotEqual(catalog_version,route_version)
        with (self.directory/"sql_examples/boost_candidates.sql").open("a") as stream:
            stream.write("\n-- 新版本\n")
        self.assertNotEqual(route_version,knowledge.read("weekly_report")["knowledge_id"])

    def test_read_does_not_silently_ignore_unknown_entries_or_topics(self):
        for function in (lambda:knowledge.read("not-a-topic"),lambda:knowledge.read(entry_ids=["missing"]),
                         lambda:knowledge.read(entry_ids="metric.viewer_uv"),lambda:knowledge.search(tags="SQL"),
                         lambda:knowledge.search(query="")):
            with self.subTest(function=function),self.assertRaises(ToolError):
                function()

    def test_broken_routes_dependencies_and_source_references_fail_closed(self):
        cases=[
            ("routes.json",lambda value:value["topics"]["weekly_report"]["entries"].append("missing")),
            ("catalog.json",lambda value:value["entries"][0]["requires"].append("missing")),
            ("catalog.json",lambda value:value["entries"][0]["requires"].append(value["entries"][0]["id"])),
            ("catalog.json",lambda value:value["entries"][0]["source"].update(path="../README.md")),
            ("catalog.json",lambda value:value["entries"][0]["source"].update(pointer="/metrics/missing")),
            ("catalog.json",lambda value:next(e for e in value["entries"] if e["id"]=="rule.common")["source"].update(heading="不存在的章节")),
        ]
        for name,mutate in cases:
            with self.subTest(name=name,mutate=mutate):
                path=self.directory/name
                original=path.read_text()
                try:
                    self.change(name,mutate)
                    with self.assertRaises(ToolError) as raised:
                        knowledge.read("weekly_report")
                    self.assertEqual(raised.exception.code,"INVALID_KNOWLEDGE_INDEX")
                finally:
                    path.write_text(original)


if __name__=="__main__":
    unittest.main()
