import sqlite3, json, os
from datetime import datetime, timedelta, timezone
from config import Config

def connect():
    db=sqlite3.connect(Config.DATABASE)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(Config.DATABASE)),exist_ok=True)
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS deployments(
          id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT NOT NULL, commit_sha TEXT NOT NULL,
          environment TEXT NOT NULL, status TEXT NOT NULL, duration_seconds INTEGER DEFAULT 0,
          risk_score INTEGER DEFAULT 0, change_type TEXT DEFAULT 'routine', created_at TEXT NOT NULL,
          source TEXT DEFAULT 'prototype', details TEXT DEFAULT '{}');
        CREATE TABLE IF NOT EXISTS incidents(
          id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, service TEXT NOT NULL,
          symptom TEXT NOT NULL, root_cause TEXT NOT NULL, prevention TEXT NOT NULL,
          severity TEXT DEFAULT 'medium', occurred_at TEXT NOT NULL, tags TEXT DEFAULT '[]');
        CREATE TABLE IF NOT EXISTS agent_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, title TEXT NOT NULL,
          message TEXT NOT NULL, created_at TEXT NOT NULL, metadata TEXT DEFAULT '{}');
        CREATE TABLE IF NOT EXISTS risk_assessments(
          id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT NOT NULL, change_type TEXT NOT NULL,
          score INTEGER NOT NULL, factors TEXT NOT NULL, recommendation TEXT NOT NULL,
          created_at TEXT NOT NULL);
        """)
        count=db.execute("SELECT COUNT(*) n FROM deployments").fetchone()["n"]
        if count==0:
            seed(db)

def seed(db):
    ts=datetime.now(timezone.utc)
    deps=[
      ("checkout-api","a83f91c","Production","rolled_back",252,72,"database migration"),
      ("user-service","d2e17ab","Production","succeeded",168,18,"routine patch"),
      ("billing-worker","e91bc42","Production","succeeded",185,42,"configuration update"),
      ("search-api","4c90e1d","Staging","succeeded",141,16,"routine patch"),
      ("checkout-api","91f2a60","Production","succeeded",197,38,"dependency upgrade"),
      ("notification-api","a77c120","Production","succeeded",156,21,"routine patch")]
    for i,d in enumerate(deps):
        db.execute("INSERT INTO deployments(service,commit_sha,environment,status,duration_seconds,risk_score,change_type,created_at,source) VALUES(?,?,?,?,?,?,?,?,?)",(*d,(ts-timedelta(hours=i*5)).isoformat(timespec="seconds"),"seed"))
    incidents=[
      ("INC-204","checkout-api","Migration timeout","Lock contention on orders table","Run migration dry-run; deploy with a 5% canary","high",["migration","timeout","database"]),
      ("INC-198","billing-worker","Elevated queue lag","Worker concurrency mismatch","Load-test queue throughput before release","medium",["queue","performance"]),
      ("INC-191","user-service","HTTP 502 spike","Readiness endpoint changed unexpectedly","Validate readiness and liveness endpoints","high",["healthcheck","http"]),
      ("INC-177","search-api","Latency regression","Unindexed query introduced","Add query-plan regression test","medium",["database","latency"])]
    for x in incidents:
        db.execute("INSERT INTO incidents(code,service,symptom,root_cause,prevention,severity,occurred_at,tags) VALUES(?,?,?,?,?,?,?,?)",(x[0],x[1],x[2],x[3],x[4],x[5],(ts-timedelta(days=3+len(x[0]))).isoformat(timespec="seconds"),json.dumps(x[6])))
    db.execute("INSERT INTO agent_events(event_type,title,message,created_at) VALUES(?,?,?,?)",("learning","Failure pattern indexed","INC-204 linked to checkout-api migration signature.",ts.isoformat(timespec="seconds")))
