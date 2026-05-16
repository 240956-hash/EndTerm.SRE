import os
import socket

import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, CONTENT_TYPE_LATEST, generate_latest

from metrics import install_metrics_middleware

app = FastAPI(title="order-service")
install_metrics_middleware(app, "order-service")
order_attempts = Counter("order_create_attempts_total", "Total order create attempts")
order_failures = Counter("order_create_failures_total", "Total failed order creations")


def get_connection():
    host = os.getenv("ORDER_DB_HOST", "postgres")
    try:
        socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise RuntimeError(f"ORDER_DB_HOST '{host}' is not resolvable inside the container network") from exc

    return psycopg2.connect(
        host=host,
        port=os.getenv("ORDER_DB_PORT", "5432"),
        user=os.getenv("ORDER_DB_USER", "app"),
        password=os.getenv("ORDER_DB_PASSWORD", "app"),
        dbname=os.getenv("ORDER_DB_NAME", "shop"),
        connect_timeout=int(os.getenv("ORDER_DB_CONNECT_TIMEOUT", "3")),
    )


@app.on_event("startup")
def startup():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL CHECK (quantity > 0)
                )
                """
            )
            conn.commit()
    finally:
        conn.close()


@app.get("/health")
def health():
    return {"status": "ok", "service": "order-service"}


def charge_payment(order_id: int, quantity: int) -> dict | None:
    payment_url = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8005")
    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.post(
                f"{payment_url}/payments",
                json={"order_id": order_id, "amount": float(quantity) * 19.99},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        return None


def send_notification(user_id: int, order_id: int) -> dict | None:
    notify_url = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8006")
    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.post(
                f"{notify_url}/notify",
                json={
                    "user_id": user_id,
                    "channel": "email",
                    "subject": "Order confirmed",
                    "body": f"Your order #{order_id} has been placed successfully.",
                },
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError:
        return None


@app.post("/orders")
def create_order(payload: dict):
    order_attempts.inc()
    try:
        conn = get_connection()
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING id, user_id, product_id, quantity",
                    (payload["user_id"], payload["product_id"], payload["quantity"]),
                )
                order = cur.fetchone()
        payment = charge_payment(order["id"], order["quantity"])
        notification = send_notification(order["user_id"], order["id"])
        return {"order": order, "payment": payment, "notification": notification}
    except Exception as exc:
        order_failures.inc()
        raise HTTPException(status_code=500, detail=f"Order creation failed: {exc}") from exc


@app.get("/orders")
def list_orders():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, user_id, product_id, quantity FROM orders ORDER BY id DESC LIMIT 20")
            return {"items": cur.fetchall()}
    finally:
        conn.close()


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
