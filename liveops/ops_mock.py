"""Synthetic multi-source snapshot for weekly/campaign/traffic-boost workflows."""
import csv
import hashlib
import json
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

TABLES = {
    "users": "user_id INTEGER PRIMARY KEY, platform TEXT NOT NULL, channel TEXT NOT NULL, device_id TEXT NOT NULL",
    "streamers": "streamer_id INTEGER PRIMARY KEY, tier TEXT NOT NULL, category TEXT NOT NULL",
    "view_sessions": "session_id INTEGER PRIMARY KEY, date TEXT NOT NULL, user_id INTEGER NOT NULL REFERENCES users(user_id), streamer_id INTEGER NOT NULL REFERENCES streamers(streamer_id), duration_seconds INTEGER NOT NULL",
    "payment_attempts": "attempt_id INTEGER PRIMARY KEY, date TEXT NOT NULL, user_id INTEGER NOT NULL REFERENCES users(user_id), streamer_id INTEGER NOT NULL REFERENCES streamers(streamer_id), status TEXT NOT NULL, amount_idr INTEGER NOT NULL",
    "transactions": "transaction_id INTEGER PRIMARY KEY, attempt_id INTEGER NOT NULL UNIQUE REFERENCES payment_attempts(attempt_id), date TEXT NOT NULL, user_id INTEGER NOT NULL REFERENCES users(user_id), streamer_id INTEGER NOT NULL REFERENCES streamers(streamer_id), amount_idr INTEGER NOT NULL",
    "metadata": "key TEXT PRIMARY KEY, value TEXT NOT NULL",
}


def generate(data_dir: Path):
    data_dir.mkdir(parents=True,exist_ok=True)
    path=data_dir/"liveops.sqlite"
    if path.exists():
        raise FileExistsError("快照已存在；请使用新的 --data-dir，避免覆盖历史证据。")
    rng=random.Random(20261020)
    start,end=date(2026,9,1),date(2026,10,17)
    con=sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys=ON")
    try:
        schemas=dict(TABLES)
        schemas.update({
            "streamer_daily":"date TEXT, streamer_id INTEGER REFERENCES streamers(streamer_id), live_seconds INTEGER NOT NULL, PRIMARY KEY(date,streamer_id)",
            "campaigns":"campaign_id TEXT PRIMARY KEY, name TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL",
            "campaign_streamers":"campaign_id TEXT REFERENCES campaigns(campaign_id), streamer_id INTEGER REFERENCES streamers(streamer_id), PRIMARY KEY(campaign_id,streamer_id)",
            "traffic_boost_daily":"date TEXT, streamer_id INTEGER REFERENCES streamers(streamer_id), allocated_units INTEGER NOT NULL, PRIMARY KEY(date,streamer_id)",
        })
        for table,definition in schemas.items():
            con.execute(f"CREATE TABLE {table} ({definition})")
        users=[(uid,"Android" if rng.random()<.78 else "iOS",rng.choice(["organic","ads","referral"]),f"device-{uid}") for uid in range(1,4001)]
        con.executemany("INSERT INTO users VALUES (?,?,?,?)",users)
        streamers=[(sid,["head","mid","tail"][(sid-1)%3],["music","gaming","chat"][(sid-1)%3]) for sid in range(1,61)]
        con.executemany("INSERT INTO streamers VALUES (?,?,?)",streamers)
        con.execute("INSERT INTO campaigns VALUES ('idn-oct-mission','印尼腰尾主播任务','2026-10-08','2026-10-14')")
        campaign_ids={sid for sid,tier,_ in streamers if tier!='head'}
        con.executemany("INSERT INTO campaign_streamers VALUES ('idn-oct-mission',?)",[(sid,) for sid in sorted(campaign_ids)])
        sessions,attempts,txs,broadcasts,boosts=[],[],[],[],[]
        for offset in range((end-start).days+1):
            ds=(start+timedelta(days=offset)).isoformat()
            live={sid:rng.choice([1800,2700,3600,5400,9000,14400]) if rng.random()<.72 else 0 for sid in range(1,61)}
            broadcasts.extend((ds,sid,seconds) for sid,seconds in live.items())
            boosts.extend((ds,sid,rng.choice([0,0,200,500,1000]) if live[sid] else 0) for sid in live)
            active=[sid for sid,seconds in live.items() if seconds]
            weights=[(1.7 if "2026-10-08"<=ds<="2026-10-14" and sid in campaign_ids else 1)*(.2 if ds>="2026-10-15" and streamers[sid-1][1]=="tail" else 1) for sid in active]
            for uid in rng.sample(range(1,4001),rng.randint(700,950)):
                for _ in range(2 if rng.random()<.18 else 1):
                    sid=rng.choices(active,weights=weights,k=1)[0]
                    duration=rng.randint(15,min(live[sid],3600))
                    sessions.append((len(sessions)+1,ds,uid,sid,duration))
                    if rng.random()<.11:
                        amount=rng.choice([10000,20000,50000,100000,200000])
                        aid=len(attempts)+1
                        success=rng.random()<.95
                        attempts.append((aid,ds,uid,sid,"success" if success else "failed",amount))
                        if success:
                            txs.append((len(txs)+1,aid,ds,uid,sid,amount))
        con.executemany("INSERT INTO view_sessions VALUES (?,?,?,?,?)",sessions)
        con.executemany("INSERT INTO payment_attempts VALUES (?,?,?,?,?,?)",attempts)
        con.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?)",txs)
        con.executemany("INSERT INTO streamer_daily VALUES (?,?,?)",broadcasts)
        con.executemany("INSERT INTO traffic_boost_daily VALUES (?,?,?)",boosts)
        for table in ("view_sessions","payment_attempts","transactions","streamer_daily","traffic_boost_daily"):
            con.execute(f"CREATE INDEX idx_{table}_date ON {table}(date)")
        con.execute("CREATE INDEX idx_view_membership ON view_sessions(date,user_id,streamer_id)")
        digest=hashlib.sha256()
        counts={}
        for table in schemas:
            if table=="metadata":
                continue
            cursor=con.execute(f"SELECT * FROM {table} ORDER BY rowid")
            with (data_dir/f"{table}.csv").open("w",newline="",encoding="utf-8") as file:
                writer=csv.writer(file)
                writer.writerow([c[0] for c in cursor.description])
                n=0
                for row in cursor:
                    writer.writerow(row)
                    digest.update(json.dumps(row,separators=(",",":")).encode())
                    n+=1
                counts[table]=n
        meta={"seed":"20261020","start_date":start.isoformat(),"end_date":end.isoformat(),
              "timezone":"Asia/Jakarta","synthetic":"true","snapshot_id":digest.hexdigest(),
              "generator_version":"operations-v2","metric_version":"operations-v2","rule_version":"operations-rules-v2"}
        con.executemany("INSERT INTO metadata VALUES (?,?)",meta.items())
        con.commit()
        manifest={**meta,"row_counts":counts,"note":"周报、活动复盘和主播流量助推流程的合成多源数据。"}
        (data_dir/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
        return manifest
    finally:
        con.close()
