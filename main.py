from __future__ import annotations
import json, os, sys, time
from dataclasses import dataclass
from typing import Any
import requests

API_BASE = "https://api.supabase.com/v1"
REQUEST_TIMEOUT = 25
MAX_RETRIES = 3

@dataclass
class ProjectResult:
    ref: str
    name: str
    status: str
    database_check: str = "not_configured"
    restore: str = "not_attempted"
    detail: str = ""

def env_json(name: str) -> dict[str, str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return {}
    try:
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("expected a JSON object")
        return {str(k): str(v) for k, v in value.items()}
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{name} must be a valid JSON object") from exc

def selected_project_refs() -> set[str]:
    raw = os.getenv("SUPABASE_PROJECT_REFS", "").strip()
    return {item.strip() for item in raw.replace("\n", ",").split(",") if item.strip()}

def request_with_retry(session: requests.Session, method: str, url: str, **kwargs: Any) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = session.request(method, url, timeout=REQUEST_TIMEOUT, **kwargs)
            if response.status_code not in (429, 500, 502, 503, 504):
                return response
            last_error = RuntimeError(f"HTTP {response.status_code}: {response.text[:250]}")
        except requests.RequestException as exc:
            last_error = exc
        if attempt < MAX_RETRIES - 1:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"request failed after {MAX_RETRIES} attempts: {last_error}")

def list_projects(session: requests.Session) -> list[dict[str, Any]]:
    projects, page = [], 1
    while True:
        response = request_with_retry(session, "GET", f"{API_BASE}/projects", params={"page": page, "limit": 100})
        if response.status_code != 200:
            raise RuntimeError(f"Could not list Supabase projects (HTTP {response.status_code}): {response.text[:500]}")
        batch = response.json()
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected response from Supabase projects API")
        projects.extend(batch)
        if len(batch) < 100:
            return projects
        page += 1

def get_status(project: dict[str, Any]) -> str:
    return str(project.get("status") or "UNKNOWN").upper()

def attempt_restore(session: requests.Session, project_ref: str) -> tuple[str, str]:
    response = request_with_retry(session, "POST", f"{API_BASE}/projects/{project_ref}/restore", json={})
    if response.status_code in (200, 202, 204):
        return "requested", "restore request accepted"
    return "failed", f"restore API returned HTTP {response.status_code}: {response.text[:300]}"

def database_health_check(password: str, host: str, port: int) -> tuple[str, str]:
    try:
        import psycopg
        from psycopg.conninfo import make_conninfo
        conninfo = make_conninfo(host=host, port=port, dbname="postgres", user="postgres",
            password=password, connect_timeout=10, sslmode="require", application_name="wakey-wakey")
        with psycopg.connect(conninfo) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                if cur.fetchone() != (1,):
                    return "failed", "unexpected result from SELECT 1"
        return "ok", "read-only SELECT 1 succeeded"
    except Exception as exc:
        return "failed", f"database check failed ({type(exc).__name__})"

def main() -> int:
    token = os.getenv("SUPABASE_ACCESS_TOKEN", "").strip()
    if not token:
        print("ERROR: missing SUPABASE_ACCESS_TOKEN secret", file=sys.stderr)
        return 2
    try:
        passwords = env_json("SUPABASE_DB_PASSWORDS")
        hosts = env_json("SUPABASE_DB_HOSTS")
        port = int(os.getenv("SUPABASE_DB_PORT", "5432"))
    except (ValueError, TypeError) as exc:
        print(f"ERROR: invalid configuration: {exc}", file=sys.stderr)
        return 2
    if not 1 <= port <= 65535:
        print("ERROR: SUPABASE_DB_PORT must be between 1 and 65535", file=sys.stderr)
        return 2

    allowed_refs = selected_project_refs()
    restore_enabled = os.getenv("RESTORE_INACTIVE_PROJECTS", "false").strip().lower() == "true"
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json",
        "User-Agent": "wakey-wakey/1.0"})
    try:
        projects = list_projects(session)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    selected = []
    for project in projects:
        ref = str(project.get("ref") or project.get("id") or "")
        if not allowed_refs or ref in allowed_refs:
            selected.append(project)
    print(f"Discovered {len(projects)} project(s); selected {len(selected)} for this run.")
    results: list[ProjectResult] = []

    for project in selected:
        ref = str(project.get("ref") or project.get("id") or "")
        name = str(project.get("name") or ref or "unnamed")
        status = get_status(project)
        if not ref:
            print(f"SKIP: {name}: response did not include a project ref")
            continue
        result = ProjectResult(ref=ref, name=name, status=status)
        if status == "INACTIVE" and restore_enabled:
            try:
                result.restore, result.detail = attempt_restore(session, ref)
            except Exception as exc:
                result.restore = "failed"
                result.detail = f"restore request failed ({type(exc).__name__})"
        password = passwords.get(ref)
        if password:
            db = project.get("database") or {}
            host = hosts.get(ref) or db.get("host") or f"db.{ref}.supabase.co"
            result.database_check, detail = database_health_check(password, host, port)
            result.detail = "; ".join(filter(None, (result.detail, detail)))
        results.append(result)
        print(f"- {name} [{ref}]: status={status}, database={result.database_check}, restore={result.restore}")

    found_refs = {str(p.get("ref") or p.get("id") or "") for p in selected}
    for ref in sorted(allowed_refs - found_refs):
        print(f"WARNING: configured project ref was not found: {ref}")

    summary = {
        "projects_discovered": len(projects), "projects_selected": len(selected),
        "projects_processed": len(results),
        "database_checks_ok": sum(r.database_check == "ok" for r in results),
        "database_checks_failed": sum(r.database_check == "failed" for r in results),
        "database_checks_not_configured": sum(r.database_check == "not_configured" for r in results),
        "restore_requests": sum(r.restore == "requested" for r in results),
    }
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as file:
            file.write("# Wakey Wakey ☀️\n\n")
            for key, label in [("projects_discovered", "Projects discovered"), ("projects_selected", "Projects selected"),
                ("database_checks_ok", "Database checks successful"), ("database_checks_failed", "Database checks failed"),
                ("restore_requests", "Restore requests accepted")]:
                file.write(f"- {label}: **{summary[key]}**\n")
            file.write("\n| Project | Status | DB check | Restore |\n|---|---|---|---|\n")
            for r in results:
                file.write(f"| {r.name.replace('|', '\\|')} | {r.status} | {r.database_check} | {r.restore} |\n")
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
