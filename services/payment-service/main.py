import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import Counter, CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from metrics import install_metrics_middleware

app = FastAPI(title="payment-service")
install_metrics_middleware(app, "payment-service")
payment_attempts = Counter("payment_attempts_total", "Total payment attempts")
payment_failures = Counter("payment_failures_total", "Total failed payments")

PAYMENTS: dict[str, dict] = {}


class PaymentRequest(BaseModel):
    order_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    currency: str = "USD"


@app.get("/health")
def health():
    return {"status": "ok", "service": "payment-service"}


@app.post("/payments")
def process_payment(payload: PaymentRequest):
    payment_attempts.inc()
    simulate_failure = os.getenv("PAYMENT_SIMULATE_FAILURE", "false").lower() == "true"
    if simulate_failure:
        payment_failures.inc()
        raise HTTPException(status_code=502, detail="Payment gateway unavailable (simulated)")

    payment_id = str(uuid.uuid4())
    record = {
        "payment_id": payment_id,
        "order_id": payload.order_id,
        "amount": payload.amount,
        "currency": payload.currency,
        "status": "captured",
    }
    PAYMENTS[payment_id] = record
    return record


@app.get("/payments/{payment_id}")
def get_payment(payment_id: str):
    record = PAYMENTS.get(payment_id)
    if not record:
        raise HTTPException(status_code=404, detail="Payment not found")
    return record


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
