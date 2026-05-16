import argparse
import asyncio
import json
import time
import urllib.request


def _fetch(url: str, timeout: float, method: str, body: str | None) -> int:
    headers = {"User-Agent": "assignment6-load-test"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = body.encode("utf-8")

    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        return resp.status


async def worker(url: str, requests_per_worker: int, timeout: float, method: str, body: str | None) -> tuple[int, int]:
    ok = 0
    err = 0
    for _ in range(requests_per_worker):
        try:
            status = await asyncio.to_thread(_fetch, url, timeout, method, body)
            if 200 <= status < 500:
                ok += 1
            else:
                err += 1
        except Exception:
            err += 1
    return ok, err


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="Target URL (e.g. http://localhost/api/products/products)")
    p.add_argument("--concurrency", type=int, default=25)
    p.add_argument("--requests", type=int, default=500, help="Total requests (ignored if --duration is set)")
    p.add_argument("--duration", type=float, default=0.0, help="Run for N seconds (overrides --requests)")
    p.add_argument("--timeout", type=float, default=2.0)
    p.add_argument("--method", default="GET", choices=["GET", "POST"], help="HTTP method")
    p.add_argument(
        "--json",
        default="",
        help="JSON body for POST (example: '{\"user_id\":1,\"product_id\":2,\"quantity\":1}')",
    )
    args = p.parse_args()

    body: str | None = None
    if args.method == "POST":
        if not args.json.strip():
            raise SystemExit("For --method POST you must provide --json body")
        # Validate json early so errors are obvious.
        body = json.dumps(json.loads(args.json))

    if args.duration and args.duration > 0:
        # Run a steady-state test for better time-series visibility in Grafana.
        end_at = time.perf_counter() + args.duration
        ok = 0
        err = 0
        total = 0
        start = time.perf_counter()
        while time.perf_counter() < end_at:
            # One "batch" = concurrency requests in parallel.
            results = await asyncio.gather(*[worker(args.url, 1, args.timeout, args.method, body) for _ in range(args.concurrency)])
            ok += sum(r[0] for r in results)
            err += sum(r[1] for r in results)
            total += args.concurrency
        elapsed = time.perf_counter() - start
    else:
        per_worker = max(1, args.requests // max(1, args.concurrency))
        total = per_worker * args.concurrency

        start = time.perf_counter()
        results = await asyncio.gather(*[worker(args.url, per_worker, args.timeout, args.method, body) for _ in range(args.concurrency)])
        elapsed = time.perf_counter() - start

        ok = sum(r[0] for r in results)
        err = sum(r[1] for r in results)
    rps = total / elapsed if elapsed > 0 else 0.0

    print(f"url={args.url}")
    if args.duration and args.duration > 0:
        print(f"method={args.method} concurrency={args.concurrency} duration_s={args.duration} timeout={args.timeout}s")
    else:
        print(f"method={args.method} concurrency={args.concurrency} requests={total} timeout={args.timeout}s")
    print(f"ok={ok} err={err}")
    print(f"elapsed_s={elapsed:.3f} rps={rps:.2f}")


if __name__ == "__main__":
    asyncio.run(main())

