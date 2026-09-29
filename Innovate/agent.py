from database import connect, now
from services.risk_engine import assess
import json
def record_event(kind,title,message,metadata=None):
    with connect() as db:
        db.execute("INSERT INTO agent_events(event_type,title,message,created_at,metadata) VALUES(?,?,?,?,?)",
                   (kind,title,message,now(),json.dumps(metadata or {})))
def learn_from_incident(incident):
    record_event("learning","Failure memory updated",
      f"{incident['code']} indexed for {incident['service']}: {incident['symptom']}",
      {"incident_code":incident["code"],"service":incident["service"]})
def review_deployment(payload):
    result=assess(payload["service"],payload.get("change_type","routine patch"),
                  payload.get("environment","Production"),payload.get("change_size","medium"))
    with connect() as db:
        db.execute("INSERT INTO risk_assessments(service,change_type,score,factors,recommendation,created_at) VALUES(?,?,?,?,?,?)",
          (payload["service"],payload.get("change_type","routine patch"),result["score"],json.dumps(result["factors"]),result["recommendation"],now()))
    record_event("risk","Pre-deployment risk assessed",
       f"{payload['service']} assessed at {result['score']}/100 ({result['level']}).",
       {"service":payload["service"],"score":result["score"]})
    return result
