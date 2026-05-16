from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from metrics import install_metrics_middleware

app = FastAPI(title="auth-service")
install_metrics_middleware(app, "auth-service")
login_counter = Counter("auth_logins_total", "Total login attempts")
register_counter = Counter("auth_registrations_total", "Total registration attempts")

# Demo in-memory user store for the assignment.
# username -> {"id": int, "password": str}
USERS = {"student": {"id": 1, "password": "password123"}}
NEXT_USER_ID = 2


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "auth-service"}


@app.post("/register")
def register(payload: RegisterRequest):
    global NEXT_USER_ID
    register_counter.inc()
    username = payload.username.strip()
    password = payload.password

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if username in USERS:
        raise HTTPException(status_code=409, detail="User already exists")

    user_id = NEXT_USER_ID
    NEXT_USER_ID += 1
    USERS[username] = {"id": user_id, "password": password}
    return {"message": "User registered", "user": username, "user_id": user_id}


@app.post("/login")
def login(payload: LoginRequest):
    login_counter.inc()
    user = USERS.get(payload.username.strip())
    if user is None or payload.password != user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": f"token-{payload.username}", "user": payload.username, "user_id": user["id"]}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
