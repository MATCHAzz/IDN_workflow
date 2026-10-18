"""Snapshot quality, date and cohort validation shared by SQL tools."""
from datetime import date, timedelta

from .store import ToolError


def validate_range(start_date, end_date, meta):
    try:
        start, end = date.fromisoformat(start_date), date.fromisoformat(end_date)
    except (ValueError, TypeError):
        raise ToolError("INVALID_DATE", "日期必须为 YYYY-MM-DD") from None
    if start.isoformat() != start_date or end.isoformat() != end_date:
        raise ToolError("INVALID_DATE", "日期必须为 YYYY-MM-DD")
    if start > end:
        raise ToolError("INVALID_RANGE", "开始日期不得晚于结束日期")
    if start_date < meta["start_date"] or end_date > meta["end_date"]:
        raise ToolError("OUT_OF_RANGE", f"快照仅覆盖 {meta['start_date']} 至 {meta['end_date']}")
    if (end - start).days > 30:
        raise ToolError("RANGE_LIMIT", "单次最多查询 31 天")
    return start, end

def quality(store, start_date, end_date, meta):
    start, end = validate_range(start_date, end_date, meta)
    params = {"start": start_date, "end": end_date}
    checks = []

    def check(name, sql, expected=0, bind=params):
        value = store.query("quality_" + name, sql, bind)[0]["n"]
        checks.append({"check": name, "violations": value, "passed": value == expected})

    # Run snapshot-wide identity/referential checks; analysis-range coverage below.
    for table, key in (("users", "user_id"), ("streamers", "streamer_id"),
                       ("view_sessions", "session_id"), ("payment_attempts", "attempt_id"),
                       ("transactions", "transaction_id")):
        check(table + "_duplicate_pk", f"SELECT COUNT(*) n FROM (SELECT {key} FROM {table} GROUP BY {key} HAVING COUNT(*)>1)", bind={})
        check(table + "_null_pk", f"SELECT COUNT(*) n FROM {table} WHERE {key} IS NULL", bind={})
    for table in ("view_sessions", "payment_attempts", "transactions"):
        check(table + "_orphan", f"""SELECT COUNT(*) n FROM {table} t
              LEFT JOIN users u ON t.user_id=u.user_id LEFT JOIN streamers s ON t.streamer_id=s.streamer_id
              WHERE u.user_id IS NULL OR s.streamer_id IS NULL""", bind={})
        days = store.query("quality_coverage_" + table,
                           f"SELECT date,COUNT(*) n FROM {table} WHERE date BETWEEN :start AND :end GROUP BY date", params)
        available = {row["date"] for row in days}
        missing = [(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)
                   if (start + timedelta(days=i)).isoformat() not in available]
        # Synthetic fixture promises daily transactions. Missing days cannot silently become zeros.
        checks.append({"check": table + "_daily_coverage", "violations": len(missing),
                       "passed": not missing, "missing_dates": missing})
        all_days = store.query("quality_dates_" + table, f"SELECT date FROM {table} GROUP BY date")
        invalid = 0
        for row in all_days:
            try:
                parsed = date.fromisoformat(row["date"])
                invalid += int(parsed.isoformat() != row["date"] or row["date"] < meta["start_date"] or row["date"] > meta["end_date"])
            except (ValueError, TypeError):
                invalid += 1
        checks.append({"check": table + "_valid_dates", "violations": invalid, "passed": invalid == 0})
    check("transaction_attempt_unique", "SELECT COUNT(*) n FROM (SELECT attempt_id FROM transactions GROUP BY attempt_id HAVING COUNT(*)>1)", bind={})
    check("transaction_reconciliation", """SELECT COUNT(*) n FROM transactions t LEFT JOIN payment_attempts a ON t.attempt_id=a.attempt_id
        WHERE a.attempt_id IS NULL OR a.status!='success' OR t.date!=a.date OR t.user_id!=a.user_id
        OR t.streamer_id!=a.streamer_id OR t.amount_idr!=a.amount_idr""", bind={})
    check("missing_successful_transaction", """SELECT COUNT(*) n FROM payment_attempts a LEFT JOIN transactions t ON a.attempt_id=t.attempt_id
        WHERE a.status='success' AND t.transaction_id IS NULL""", bind={})
    check("payer_viewer_membership", """SELECT COUNT(*) n FROM transactions t WHERE NOT EXISTS
        (SELECT 1 FROM view_sessions v WHERE v.date=t.date AND v.user_id=t.user_id AND v.streamer_id=t.streamer_id)""", bind={})
    for table in ("payment_attempts", "transactions"):
        check(table + "_positive_integer_amount", f"SELECT COUNT(*) n FROM {table} WHERE amount_idr IS NULL OR typeof(amount_idr)!='integer' OR amount_idr<=0", bind={})
    check("attempt_status", "SELECT COUNT(*) n FROM payment_attempts WHERE status IS NULL OR status NOT IN ('success','failed')", bind={})
    check("user_dimensions", "SELECT COUNT(*) n FROM users WHERE platform IS NULL OR platform NOT IN ('Android','iOS') OR channel IS NULL OR channel NOT IN ('organic','ads','referral') OR device_id IS NULL OR length(device_id)=0", bind={})
    check("streamer_tier", "SELECT COUNT(*) n FROM streamers WHERE tier IS NULL OR tier NOT IN ('head','mid','tail')", bind={})
    check("watch_duration", "SELECT COUNT(*) n FROM view_sessions WHERE duration_seconds IS NULL OR duration_seconds<0", bind={})
    checks.extend(extra_checks(store, meta))
    return {"quality_status": "passed" if all(c["passed"] for c in checks) else "failed",
            "date_range": [start_date, end_date], "checks": checks}

def require_quality(store, start_date, end_date, meta):
    result = quality(store, start_date, end_date, meta)
    if result["quality_status"] != "passed":
        failures = [c["check"] for c in result["checks"] if not c["passed"]]
        raise ToolError("QUALITY_FAILED", "质量门禁失败，停止分析/导出：" + ", ".join(failures))


def extra_checks(store,meta):
    checks=[]
    queries={
        "broadcast_identity":"SELECT COUNT(*) n FROM (SELECT date,streamer_id FROM streamer_daily GROUP BY date,streamer_id HAVING COUNT(*)>1)",

        "broadcast_integrity":"SELECT COUNT(*) n FROM streamer_daily b LEFT JOIN streamers s ON b.streamer_id=s.streamer_id WHERE s.streamer_id IS NULL OR b.date IS NULL OR b.live_seconds IS NULL OR typeof(b.live_seconds)!='integer' OR b.live_seconds<0",

        "watch_live_membership":"SELECT COUNT(*) n FROM view_sessions v LEFT JOIN streamer_daily b ON v.date=b.date AND v.streamer_id=b.streamer_id WHERE b.streamer_id IS NULL OR b.live_seconds<=0 OR v.duration_seconds>b.live_seconds",

        "boost_integrity":"SELECT COUNT(*) n FROM traffic_boost_daily b LEFT JOIN streamers s ON b.streamer_id=s.streamer_id WHERE s.streamer_id IS NULL OR b.allocated_units IS NULL OR typeof(b.allocated_units)!='integer' OR b.allocated_units<0 OR b.date IS NULL",
        
        "campaign_cohort":"SELECT COUNT(*) n FROM campaign_streamers c LEFT JOIN streamers s ON c.streamer_id=s.streamer_id LEFT JOIN campaigns p ON p.campaign_id=c.campaign_id WHERE s.streamer_id IS NULL OR p.campaign_id IS NULL",
    }
    for name,sql in queries.items():
        n=store.query("operations_quality_"+name,sql)[0]["n"]
        checks.append({"check":name,"violations":n,"passed":n==0})
    expected_streamers=store.query("operations_expected_streamers","SELECT COUNT(*) n FROM streamers")[0]["n"]
    expected_days=(date.fromisoformat(meta["end_date"])-date.fromisoformat(meta["start_date"])).days+1
    for table in ("streamer_daily","traffic_boost_daily"):
        rows=store.query("operations_coverage_"+table,f"SELECT date,COUNT(*) n,COUNT(DISTINCT streamer_id) uv FROM {table} GROUP BY date")
        bad=len(rows)!=expected_days
        for row in rows:
            try:
                parsed=date.fromisoformat(row["date"])
                bad=bad or parsed.isoformat()!=row["date"] or not meta["start_date"]<=row["date"]<=meta["end_date"]
            except (TypeError,ValueError):
                bad=True
            bad=bad or row["n"]!=expected_streamers or row["uv"]!=expected_streamers
        checks.append({"check":table+"_complete_daily_ledger","violations":int(bad),"passed":not bad})
    return checks

def validate_scope(store,tier=None,campaign_id=None,streamer_id=None):
    clause=""
    params={}
    if tier is not None:
        if tier not in {"head","mid","tail"}:
            raise ToolError("INVALID_FILTER","streamer_tier只支持head/mid/tail")
        clause+=" AND s.tier=:tier"
        params["tier"]=tier
    if campaign_id is not None:
        if not isinstance(campaign_id,str) or len(campaign_id)>64:
            raise ToolError("INVALID_CAMPAIGN","campaign_id必须为短字符串")
        if not store.query("campaign_exists","SELECT campaign_id FROM campaigns WHERE campaign_id=:campaign",{"campaign":campaign_id}):
            raise ToolError("UNKNOWN_CAMPAIGN","活动不存在；先用get_data_profile查看活动清单")
        clause+=" AND s.streamer_id IN (SELECT streamer_id FROM campaign_streamers WHERE campaign_id=:campaign)"
        params["campaign"]=campaign_id
    if streamer_id is not None:
        if not isinstance(streamer_id,int) or isinstance(streamer_id,bool):
            raise ToolError("INVALID_FILTER","streamer_id必须为整数")
        if not store.query("streamer_exists","SELECT streamer_id FROM streamers WHERE streamer_id=:sid",{"sid":streamer_id}):
            raise ToolError("UNKNOWN_STREAMER","主播不存在")
        clause+=" AND s.streamer_id=:sid"
        params["sid"]=streamer_id
    return clause,params
