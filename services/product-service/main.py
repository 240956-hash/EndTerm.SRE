from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import Counter, CONTENT_TYPE_LATEST, generate_latest

from metrics import install_metrics_middleware

app = FastAPI(title="product-service")
install_metrics_middleware(app, "product-service")
product_requests = Counter("product_requests_total", "Total product list requests")

PRODUCTS = [
    {"id": 1, "name": "Keyboard", "price": 49.99},
    {"id": 2, "name": "Mouse", "price": 19.99},
    {"id": 3, "name": "Monitor", "price": 199.99},
]


@app.get("/health")
def health():
    return {"status": "ok", "service": "product-service"}


@app.get("/products")
def get_products():
    product_requests.inc()
    return {"items": PRODUCTS}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
