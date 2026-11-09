# Wakey Wakey ☀️

A small GitHub Actions project that inventories all Supabase projects visible to your Personal Access Token, runs optional read-only database health checks, and can request restoration for paused projects.

## What it does

- Runs every 6 hours (UTC), plus manual dispatch.
- Discovers projects through the Supabase Management API.
- Checks project state.
- Optionally attempts to restore projects reported as `INACTIVE`.
- Executes read-only `SELECT 1` checks for projects whose database credentials are configured.
- Writes a GitHub Actions job summary.

> **Important:** Supabase's inactivity pausing is based on user database activity over a rolling 7-day period. Supabase says a few user requests each day is typically sufficient, but does not guarantee a project will never be paused. See [Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing).
>
> A GitHub run every six hours is a monitoring cadence, not a guarantee that every request counts as qualifying user activity. This tool does not bypass Supabase limits or policies.

## Setup

### 1. Create a Supabase Personal Access Token

Create a scoped PAT in Supabase account settings. Grant the projects-read permission for inventory. If you intend to enable restoration, grant the required project-management permission as well. Prefer a scoped token with the least privilege.

Add it in GitHub:

**Settings → Secrets and variables → Actions → New repository secret**

- Name: `SUPABASE_ACCESS_TOKEN`
- Value: your PAT

### 2. Configure database keep-alive checks

Database queries need each project's database password. Add another GitHub repository secret:

- Name: `SUPABASE_DB_PASSWORDS`
- Value: JSON object mapping project ref to password, for example:
  `{"abcdefghijklmnopqrst":"your-db-password"}`

Optional:

- `SUPABASE_DB_HOSTS`: JSON map of project ref to database hostname. If absent, the hostname returned by Supabase's project list is used, with `db.<ref>.supabase.co` as fallback.
- Repository variable `SUPABASE_DB_PORT`: defaults to `5432`.

Use direct database connection hosts where supported. Direct database connectivity may require IPv6; if your runner cannot reach it, configure a supported session pooler hostname/port and the matching username format. This starter supports the default `postgres` user and common direct connections; pooler-specific usernames require adapting the configuration/code.

### 3. Optional restore

By default, restore attempts are disabled.

Add repository variable:

- Name: `RESTORE_INACTIVE_PROJECTS`
- Value: `true`

Only enable this after confirming the PAT has the necessary permissions. The Management API restore endpoint can accept restoration requests, but a successful request does not mean the database is immediately ready. The next scheduled health checks will report readiness.

### 4. Enable Actions

Open the **Actions** tab and enable workflows if GitHub prompts you. Run **Wakey Wakey** manually once to verify the PAT and connectivity.

## Run locally

Python 3.11+:

```bash
python -m pip install -r requirements.txt
SUPABASE_ACCESS_TOKEN=your_pat python main.py
```

## Security

- No credentials are committed to source.
- Database checks run only `SELECT 1`.
- Secrets are never printed in logs.
- The workflow has read-only repository permissions.
- This repository is public, so never place PATs, database passwords, or service-role keys in files or commits.

## References

- [List all projects API](https://supabase.com/docs/reference/api/v1-list-all-projects)
- [Management API authentication](https://supabase.com/docs/reference/api/introduction)
- [Restore a project API](https://supabase.com/docs/reference/api/v1-restore-a-project)
- [Free project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
