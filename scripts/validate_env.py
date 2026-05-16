import os
import socket
import sys


def fail(msg: str) -> None:
    print(f"[validate_env] ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    # Focused on preventing the Assignment 4 incident class:
    # wrong/invalid DB hostname for order-service.
    host = os.getenv("ORDER_DB_HOST", "postgres")
    if not host or host.strip() == "":
        fail("ORDER_DB_HOST is empty")

    # Note: service names like "postgres" resolve only *inside* the docker compose network,
    # so host-side DNS resolution will fail even when configuration is correct.
    # We treat the expected compose service name as valid, and apply DNS checks to custom hosts.
    if host != "postgres":
        try:
            socket.getaddrinfo(host, None)
        except socket.gaierror:
            fail(f"ORDER_DB_HOST '{host}' is not resolvable (did you typo it, e.g. 'postgres-wrong'?)")

    port = os.getenv("ORDER_DB_PORT", "5432")
    if not port.isdigit():
        fail(f"ORDER_DB_PORT must be numeric, got '{port}'")

    print("[validate_env] OK")


if __name__ == "__main__":
    main()

