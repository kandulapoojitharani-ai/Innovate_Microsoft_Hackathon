"""Explainable baseline risk engine. Replace with a trained model after collecting labeled data."""
from database import connect
WEIGHTS={"database migration":34,"dependency upgrade":22,"configuration update":18,"routine patch":8,"feature release":14}
def assess(service, change_type, environment="Production", change_size="medium"):
    score=WEIGHTS.get(change_type.lower(),14)
    reasons=[]
    if change_type.lower()=="database migration":
        score+=16; reasons.append({"name":"Migration pattern","points":50,"evidence":"Similar to historical migration timeout INC-204."})
    else:
        reasons.append({"name":"Change category","points":score,"evidence":f"Baseline weight for {change_type}."})
    if change_size=="large":
        score+=18; reasons.append({"name":"Change size","points":18,"evidence":"Large change surface increases uncertainty."})
    elif change_size=="small":
        score-=5; reasons.append({"name":"Change size","points":-5,"evidence":"Small change surface."})
    else: reasons.append({"name":"Change size","points":8,"evidence":"Medium change surface."}); score+=8
    if environment.lower()=="production":
        score+=12; reasons.append({"name":"Environment","points":12,"evidence":"Production release has higher impact."})
    else: reasons.append({"name":"Environment","points":0,"evidence":"Non-production environment."})
    with connect() as db:
        prior=db.execute("SELECT COUNT(*) n FROM deployments WHERE service=? AND status='rolled_back'",(service,)).fetchone()["n"]
    stability=min(prior*6,18)
    if stability: score+=stability
    reasons.append({"name":"Service history","points":stability,"evidence":f"{prior} recorded rollback(s) for this service."})
    score=max(0,min(100,score))
    level="low" if score<30 else "medium" if score<60 else "high"
    recommendation=("Proceed with standard health checks." if level=="low" else
      "Use staged rollout and monitor latency and error rate." if level=="medium" else
      "Pause for review; run a migration dry-run and 5% canary with rollback guardrails.")
    return {"score":score,"level":level,"factors":reasons,"recommendation":recommendation,"model":"explainable-heuristic-v1"}
