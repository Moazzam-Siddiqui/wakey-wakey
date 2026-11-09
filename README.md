# Wakey Wakey ☀️

A small GitHub Actions service that checks every Supabase project in your account and helps keep eligible Free projects from being paused due to inactivity.

## What it does

- Runs every 6 hours (UTC) and can also be started manually.
- Discovers all projects visible to a Supabase Personal Access Token (PAT).
- Reports each project's status.
- Sends a lightweight, read-only SQL health query to configured projects with database passwords.
- Optionally requests restoration for projects reported as inactive, when enabled.
- Writes a JSON summary to the Actions job summary.

> **Important limitations**
>
> - Supabase's inactivity pause policy and project restoration behaviour are controlled by Supabase. This tool cannot guarantee that a project will never be paused.
> - A Management API project listing does not prove a database is reachable. A database health query requires the project's database password and its direct connection URL/host.
> - The Management API restore endpoint may be unavailable for some project states/plans or require additional permissions. Failures are reported, not hidden.
> - This project does not attempt to bypass quotas, billing, platform restrictions, or Supabase policies.

## Setup

### 1. Create a Supabase Personal Access Token

Create a PAT in your Supabase account settings. Give it only the permissions required to list and manage your projects. Store it as a GitHub Actions secret named:

- `SUPABASE_ACCESS_TOKEN`

Never commit the token to this repository.

### 2. Configure per-project database checks

To run actual database queries, add these GitHub repository secrets:

- `SUPABASE_DB_PASSWORDS`: JSON object mapping project ref to database password, e.g. `{"projectref1":"password1","projectref2":"password2"}`
- `SUPABASE_DB_HOSTS` (optional): JSON object mapping project ref to direct database hostname. If omitted, the standard Supabase hostname is used.
- `SUPABASE_DB_PORT` (optional): defaults to `5432`.

Use GitHub Secrets, never plaintext workflow variables. If you do not configure database passwords, the run still inventories all projects and reports their states, but cannot issue SQL keep-alive queries.

Use direct database connection hosts, not pooler hosts, where possible. Network restrictions or IPv6-only direct endpoints can make a runner unable to connect; those failures are reported.

### 3. Optional restore behaviour

Set repository variable `RESTORE_INACTIVE_PROJECTS` to `true` only after reviewing the behaviour and confirming your PAT permissions. The default is `false`. When enabled, Wakey Wakey attempts the Supabase Management API restore operation for projects identified as inactive/paused, then rechecks project status.

### 4. Enable GitHub Actions

Go to **Actions** in the repository and enable workflows if GitHub prompts you. The workflow runs every 6 hours and supports manual dispatch.

## Run locally

Python 3.11+:

```bash
python -m pip install -r requirements.txt
SUPABASE_ACCESS_TOKEN=your_pat python main.py
```

For database checks, also set `SUPABASE_DB_PASSWORDS` as a JSON string in your environment.

## Security

- No credentials are stored in source files.
- SQL health checks are read-only: `SELECT 1`.
- Database passwords are never printed.
- The workflow grants only read access to repository contents.
- Public repository means source code is public; secrets configured in GitHub Actions remain encrypted and are not exposed to the repository.

## Project structure

```
.
├── .github/workflows/wakey-wakey.yml
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Supabase documentation

- [Management API](https://supabase.com/docs/reference/api/introduction)
- [Projects API](https://supabase.com/docs/reference/api/v1-list-all-projects)
- [Restore project API](https://supabase.com/docs/reference/api/v1-restore-a-project)
- [Pausing projects](https://supabase.com/docs/guides/platform/ pausing-projects)

