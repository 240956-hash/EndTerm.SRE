import time

from prometheus_client import Histogram

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.5, 1.0, 2.5),
)


def install_metrics_middleware(app, service_name: str) -> None:
    @app.middleware("http")
    async def record_request_latency(request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        path = request.url.path
        if path != "/metrics":
            REQUEST_LATENCY.labels(
                service=service_name,
                method=request.method,
                path=path,
            ).observe(time.perf_counter() - start)
        return response
