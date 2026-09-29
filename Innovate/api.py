from flask import Blueprint, request, jsonify
from database import connect, now
from services.agent import review_deployment, record_event, learn_from_incident
import json, re
api=Blueprint("api",__name__)
def rowdicts(rows): return [dict(r) for r in rows]
@api.get("/overview")
def overview():
    with connect() as db:
        total=db.execute("SELECT COUNT(*) n FROM deployments").fetchone()["n"]
        succeeded=db.execute("SELECT COUNT(*) n FROM deployments WHERE status='succeeded'").fetchone()["n"]
        rollbacks=db.execute("SELECT COUNT(*) n FROM deployments WHERE status='rolled_back'").fetchone()["n"]
        incidents=db.execute("SELECT COUNT(*) n FROM incidents").fetchone()["n"]
        patterns=db.execute("SELECT COUNT(*) n FROM incidents").fetchone()["n"]
        recent=rowdicts(db.execute("SELECT * FROM deployments ORDER BY id DESC LIMIT 8").fetchall())
        events=rowdicts(db.execute("SELECT * FROM agent_events ORDER BY id DESC LIMIT 8").fetchall())
    return jsonify({"metrics":{"total_deployments":total,"success_rate":round(succeeded/total*100,1) if total else 0,"rollbacks":rollbacks,"incidents":incidents,"patterns":patterns},"deployments":recent,"events":events})
@api.get("/deployments")
def deployments():
    env=request.args.get("environment")
    with connect() as db:
        if env and env!="All":
            rows=db.execute("SELECT * FROM deployments WHERE environment=? ORDER BY id DESC",(env,)).fetchall()
        else: rows=db.execute("SELECT * FROM deployments ORDER BY id DESC LIMIT 100").fetchall()
    return jsonify(rowdicts(rows))
@api.post("/deployments")
def create_deployment():
    p=request.get_json(silent=True) or {}
    service=str(p.get("service","")).strip()
    if not service or len(service)>80: return jsonify({"error":"service is required (max 80 chars)"}),400
    change=p.get("change_type","routine patch")
    env=p.get("environment","Staging")
    if env not in ("Production","Staging","Development"): return jsonify({"error":"Invalid environment"}),400
    risk=review_deployment({"service":service,"change_type":change,"environment":env,"change_size":p.get("change_size","medium")})
    sha=re.sub(r"[^a-f0-9]","",str(p.get("commit_sha",""))[:12].lower()) or "demo000"
    status="blocked" if risk["score"]>=75 and p.get("enforce_guardrail",True) else "running"
    with connect() as db:
        cur=db.execute("INSERT INTO deployments(service,commit_sha,environment,status,duration_seconds,risk_score,change_type,created_at,source,details) VALUES(?,?,?,?,?,?,?,?,?,?)",
         (service,sha,env,status,0,risk["score"],change,now(),"api",json.dumps({"recommendation":risk["recommendation"]})))
        dep=dict(db.execute("SELECT * FROM deployments WHERE id=?",(cur.lastrowid,)).fetchone())
    record_event("deployment","Deployment simulation created",f"{service} entered {status} state.",{"deployment_id":dep["id"]})
    return jsonify({"deployment":dep,"risk":risk}),201
@api.post("/deployments/<int:dep_id>/complete")
def complete(dep_id):
    p=request.get_json(silent=True) or {}; status=p.get("status","succeeded")
    if status not in ("succeeded","rolled_back","failed"): return jsonify({"error":"status must be succeeded, rolled_back, or failed"}),400
    with connect() as db:
        cur=db.execute("UPDATE deployments SET status=?,duration_seconds=? WHERE id=?",(status,max(0,int(p.get("duration_seconds",180))),dep_id))
        if cur.rowcount==0:return jsonify({"error":"deployment not found"}),404
        dep=dict(db.execute("SELECT * FROM deployments WHERE id=?",(dep_id,)).fetchone())
    record_event("deployment","Deployment status updated",f"{dep['service']} is now {status}.",{"deployment_id":dep_id})
    return jsonify(dep)
@api.get("/incidents")
def incidents():
    q=request.args.get("q","").lower()
    with connect() as db: rows=rowdicts(db.execute("SELECT * FROM incidents ORDER BY id DESC").fetchall())
    return jsonify([r for r in rows if not q or q in " ".join([str(v) for v in r.values()]).lower()])
@api.post("/incidents")
def add_incident():
    p=request.get_json(silent=True) or {}
    required=("code","service","symptom","root_cause","prevention")
    if any(not str(p.get(k,"")).strip() for k in required):return jsonify({"error":"code, service, symptom, root_cause and prevention are required"}),400
    try:
        with connect() as db:
            db.execute("INSERT INTO incidents(code,service,symptom,root_cause,prevention,severity,occurred_at,tags) VALUES(?,?,?,?,?,?,?,?)",
             (p["code"],p["service"],p["symptom"],p["root_cause"],p["prevention"],p.get("severity","medium"),p.get("occurred_at",now()),json.dumps(p.get("tags",[]))))
    except Exception as e:return jsonify({"error":"Could not save incident; code may already exist."}),409
    item={"code":p["code"],"service":p["service"],"symptom":p["symptom"]}
    learn_from_incident(item)
    return jsonify({"message":"Incident stored in failure memory","incident":item}),201
@api.post("/risk")
def risk():
    p=request.get_json(silent=True) or {}
    if not p.get("service"):return jsonify({"error":"service is required"}),400
    return jsonify(review_deployment(p))
@api.get("/events")
def events():
    with connect() as db: rows=rowdicts(db.execute("SELECT * FROM agent_events ORDER BY id DESC LIMIT 100").fetchall())
    return jsonify(rows)
@api.get("/memory/stats")
def memory_stats():
    with connect() as db:
        rows=rowdicts(db.execute("SELECT service,COUNT(*) incidents FROM incidents GROUP BY service ORDER BY incidents DESC").fetchall())
    return jsonify({"by_service":rows,"total":sum(r["incidents"] for r in rows)})
