import json
import os
from datetime import datetime, timezone

import redis
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from metrics import install_metrics_middleware

app = FastAPI(title="notification-service")
install_metrics_middleware(app, "notification-service")
notification_sent = Counter("notifications_sent_total", "Total notifications sent")
notification_failures = Counter("notification_failures_total", "Total notification delivery failures")

REDIS_CHANNEL = "shop.notifications"
NOTIFICATIONS: list[dict] = []


class NotifyRequest(BaseModel):
    user_id: int = Field(gt=0)
    channel: str = "email"
    subject: str
    body: str


def redis_client() -> redis.Redis:
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
        socket_connect_timeout=3,
    )


@app.get("/health")
def health():
    try:
        redis_client().ping()
        redis_ok = True
    except redis.RedisError:
        redis_ok = False
    status = "ok" if redis_ok else "degraded"
    return {"status": status, "service": "notification-service", "redis": redis_ok}


@app.post("/notify")
def notify(payload: NotifyRequest):
    record = {
        "user_id": payload.user_id,
        "channel": payload.channel,
        "subject": payload.subject,
        "body": payload.body,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        client = redis_client()
        client.publish(REDIS_CHANNEL, json.dumps(record))
        client.lpush("shop:notifications", json.dumps(record))
        client.ltrim("shop:notifications", 0, 99)
    except redis.RedisError as exc:
        notification_failures.inc()
        raise HTTPException(status_code=503, detail=f"Notification broker unavailable: {exc}") from exc

    notification_sent.inc()
    NOTIFICATIONS.insert(0, record)
    NOTIFICATIONS[:] = NOTIFICATIONS[:20]
    return {"status": "queued", "notification": record}


@app.get("/notifications")
def list_notifications():
    try:
        client = redis_client()
        items = client.lrange("shop:notifications", 0, 19)
        return {"items": [json.loads(item) for item in items]}
    except redis.RedisError:
        return {"items": NOTIFICATIONS}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
