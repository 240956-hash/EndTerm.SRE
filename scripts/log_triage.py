import argparse
import re
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Pattern:
    name: str
    regex: re.Pattern
    hint: str


PATTERNS: list[Pattern] = [
    Pattern(
        name="db_dns_resolution_failed",
        regex=re.compile(r"(could not translate host name|Name or service not known|gaierror|not resolvable)", re.I),
        hint="Похоже, неверный hostname БД. Проверь `.env` (ORDER_DB_HOST=postgres) и сеть docker compose.",
    ),
    Pattern(
        name="db_connection_refused",
        regex=re.compile(r"(connection refused|could not connect to server|is the server running)", re.I),
        hint="БД не готова/недоступна. Проверь `docker compose ps`, healthcheck postgres и зависимости.",
    ),
    Pattern(
        name="db_auth_failed",
        regex=re.compile(r"(password authentication failed|authentication failed|no pg_hba\.conf entry)", re.I),
        hint="Проблема с учётными данными/доступом к БД. Проверь ORDER_DB_USER/ORDER_DB_PASSWORD и POSTGRES_*.",
    ),
    Pattern(
        name="uvicorn_crash_loop",
        regex=re.compile(r"(Application startup failed|Traceback \(most recent call last\)|ERROR:.*Exception)", re.I),
        hint="Сервис падает при старте. Посмотри traceback и проверь переменные окружения/миграции/зависимости.",
    ),
    Pattern(
        name="prometheus_rule_load_failed",
        regex=re.compile(r"(error loading rules|parse error|failed to evaluate)", re.I),
        hint="Проблема с alert rules. Проверь `prometheus/alerts.yml` и UI Prometheus (Status → Rules).",
    ),
]


def run_compose_logs(services: list[str], tail: int) -> str:
    cmd = ["docker", "compose", "logs", "--no-color", f"--tail={tail}"]
    cmd.extend(services)
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.stdout


def main() -> int:
    p = argparse.ArgumentParser(description="Simple log-based troubleshooting automation (pattern triage).")
    p.add_argument("--tail", type=int, default=400, help="How many log lines to inspect per service (default: 400)")
    p.add_argument(
        "--services",
        nargs="*",
        default=[],
        help="Optional compose service names (default: all services)",
    )
    args = p.parse_args()

    logs = run_compose_logs(args.services, args.tail)
    findings: list[tuple[Pattern, list[str]]] = []

    lines = logs.splitlines()
    for pat in PATTERNS:
        matched = []
        for line in lines:
            if pat.regex.search(line):
                matched.append(line)
                if len(matched) >= 10:
                    break
        if matched:
            findings.append((pat, matched))

    if not findings:
        print("[log_triage] OK: patterns not found in recent logs.")
        return 0

    print("[log_triage] FOUND potential issues:\n")
    for pat, matched in findings:
        print(f"- {pat.name}")
        print(f"  hint: {pat.hint}")
        print("  examples:")
        for m in matched[:5]:
            print(f"   - {m}")
        print()

    # Non-zero exit so it can be used in automation/CI-like checks.
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

