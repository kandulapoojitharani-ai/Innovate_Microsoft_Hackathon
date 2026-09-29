from flask import Blueprint, request, jsonify, current_app
from services.agent import record_event
import hmac, hashlib
webhooks=Blueprint("webhooks",__name__)
@webhooks.post("/deployment")
def deployment_webhook():
    """Generic receiver example. Set PULSEOPS_WEBHOOK_SECRET to enable HMAC verification."""
    secret=current_app.config.get("WEBHOOK_SECRET")
    raw=request.get_data()
    if secret:
        supplied=request.headers.get("X-PulseOps-Signature","")
        expected="sha256="+hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
        if not hmac.compare_digest(supplied,expected):return jsonify({"error":"invalid signature"}),401
    payload=request.get_json(silent=True) or {}
    if not payload.get("service"):return jsonify({"error":"service is required"}),400
    record_event("webhook","CI/CD webhook received",f"Received event for {payload['service']}.",payload)
    return jsonify({"received":True,"note":"Webhook event logged; map provider payloads before production use."}),202
