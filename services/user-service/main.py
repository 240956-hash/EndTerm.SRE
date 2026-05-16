from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import Counter, CONTENT_TYPE_LATEST, generate_latest

from metrics import install_metrics_middleware

app = FastAPI(title="user-profile-service")
install_metrics_middleware(app, "user-profile-service")
profile_requests = Counter("user_profile_requests_total", "Total profile lookups")


@app.get("/health")
def health():
    return {"status": "ok", "service": "user-profile-service"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    profile_requests.inc()
    return {
        "id": user_id,
        "name": f"user-{user_id}",
        "email": f"user-{user_id}@shop.demo",
        "role": "customer",
    }


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
