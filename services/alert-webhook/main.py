"""Minimal webhook receiver so Alertmanager has a working receiver in demo mode."""
import json
from datetime import datetime, timezone

from fastapi import FastAPI, Request

app = FastAPI(title="alert-webhook")
ALERTS: list[dict] = []


@app.get("/health")
def health():
    return {"status": "ok", "alerts_buffered": len(ALERTS)}


@app.post("/alerts")
async def receive_alerts(request: Request):
    payload = await request.json()
    entry = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "alerts": payload.get("alerts", []),
        "status": payload.get("status"),
    }
    ALERTS.insert(0, entry)
    ALERTS[:] = ALERTS[:50]
    print(json.dumps(entry, indent=2), flush=True)
    return {"status": "ok"}


@app.get("/alerts")
def list_alerts():
    return {"items": ALERTS}
