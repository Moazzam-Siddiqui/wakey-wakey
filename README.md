# Wakey Wakey ☀️

**Help your Supabase projects stay awake — automatically.**

Wakey Wakey is a free, open-source helper. It runs on GitHub Actions, checks the Supabase projects you choose, and can:

- Check whether a project is active or paused.
- Ask Supabase to restore a selected project when it is inactive.
- Run a tiny, read-only database query (SELECT 1) when you add its database password.
- Show a report after every run.

It runs every **6 hours**. Your computer can be off.

> **Important:** This is a best-effort helper, not a promise that Supabase will never pause a project. Supabase controls its own pausing rules. A restore request can take time, and an accepted request does not mean the project is ready immediately.

---

## 🚀 Set it up — step by step

You need a GitHub account and a Supabase account.

### 1. Make your own copy

1. Open this repository.
2. Click **Fork** near the top-right.
3. Keep the suggested name or choose your own.
4. Open your new copy.

A fork is your own copy. You can change it without changing the original project.

### 2. Make a Supabase access token

1. Sign in to [Supabase](https://supabase.com/dashboard).
2. Open your account settings.
3. Find **Access Tokens**.
4. Create a new Personal Access Token (PAT).
5. Give it permission to read your project list. If you want automatic restore, also give it the project-management permission needed to restore projects.
6. Copy the token.

**Keep this token private.** It is like a password. Never put it in a code file or public message.

### 3. Give GitHub the token safely

1. Open your fork on GitHub.
2. Click **Settings**.
3. Open **Secrets and variables → Actions**.
4. Under **Repository secrets**, click **New repository secret**.
5. Name it: SUPABASE_ACCESS_TOKEN
6. Paste your token as the value.
7. Click **Add secret**.

A GitHub secret is a private value. GitHub hides it from normal logs.

### 4. Choose the projects

1. In Supabase, open a project.
2. Find its **Reference ID** in Project Settings → General.
3. Copy the Reference ID.
4. In GitHub, open **Settings → Secrets and variables → Actions → Variables**.
5. Click **New repository variable**.
6. Name it: SUPABASE_PROJECT_REFS
7. Paste the Reference IDs, separated by commas:

your_first_project_ref,your_second_project_ref

Only projects in this list will be checked or restored. If you leave this variable empty, all projects visible to your token will be selected.

**This repository owner's current selection:** rhvsvrrzklquryzfeall,qxrszwipfvvhvfpbsabe. The Agentic Workflow project is intentionally excluded. When you fork this project, replace these refs with your own.

### 5. Add database passwords (recommended)

This lets Wakey Wakey run the small database check.

1. In Supabase, open a project.
2. Go to **Project Settings → Database**.
3. Find or reset its database password.
4. In GitHub, open **Settings → Secrets and variables → Actions → Secrets**.
5. Click **New repository secret**.
6. Name it: SUPABASE_DB_PASSWORDS
7. Set the value to a JSON object like this:

    {
      "your_first_project_ref": "your_first_database_password",
      "your_second_project_ref": "your_second_database_password"
    }

Replace the example text with your real values. Do not copy the example literally.

You may also add a secret named SUPABASE_DB_HOSTS if you need custom database hostnames. It uses the same JSON format and project refs as keys. If you do not add it, Wakey Wakey tries the hostname Supabase returns, then db.PROJECT_REF.supabase.co.

The database check only runs SELECT 1. It does not change your tables or data.

### 6. Turn on GitHub Actions

1. Open the **Actions** tab in your fork.
2. If GitHub asks, click **I understand my workflows, go ahead and enable them**.
3. Choose **Wakey Wakey**.
4. Click **Run workflow** to test it.

After that, GitHub runs it automatically every 6 hours. Your computer can stay off.

---

## 🧸 What do the results mean?

| Result | Simple meaning |
|---|---|
| ACTIVE_HEALTHY | Supabase says the project is active. |
| INACTIVE | Supabase says the project is paused/inactive. |
| restore=requested | Wakey Wakey asked Supabase to restore it. Wait and check again. |
| database=ok | The tiny database check worked. |
| database=not_configured | No database password was added for this project. |
| database=failed | The database check could not connect. Check the password and host. |

To see the report, open **Actions → Wakey Wakey → latest run**. Click the job and open its **Summary**.

## ⚙️ Settings

| Name | Where to add it | What it does |
|---|---|---|
| SUPABASE_ACCESS_TOKEN | Secret | Lets the tool see your Supabase projects. Required. |
| SUPABASE_PROJECT_REFS | Variable | Comma-separated project list. Empty means all projects. |
| SUPABASE_DB_PASSWORDS | Secret | Passwords for read-only database checks. Optional. |
| SUPABASE_DB_HOSTS | Secret | Custom database hosts. Optional. |
| SUPABASE_DB_PORT | Variable | Database port. Defaults to 5432. |

Automatic restore requests are enabled in this repository's workflow. To turn them off, edit .github/workflows/wakey-wakey.yml and change RESTORE_INACTIVE_PROJECTS: "true" to "false".

## ❓ If something goes wrong

- **No projects appear:** Check that SUPABASE_ACCESS_TOKEN is saved as a GitHub secret and can read your project list.
- **Restore fails:** Check that your token has permission to restore projects. Read the error in the Actions log.
- **Database says not configured:** Add the project's password to SUPABASE_DB_PASSWORDS.
- **Database connection fails:** Check the password and host. Some networks need a Supabase session-pooler connection instead of a direct connection.
- **Nothing runs automatically:** Make sure GitHub Actions is enabled. Scheduled runs can sometimes start late.

## 🔒 Keep your account safe

- Never commit access tokens, database passwords, or service-role keys.
- Keep private values in GitHub Actions Secrets.
- Database checks run only SELECT 1.
- The workflow only needs read access to this GitHub repository.
- If SUPABASE_PROJECT_REFS is set, only those projects are processed.

## 🧑‍💻 Run it on your computer

You need Python 3.11 or newer. Install the packages with:

    python -m pip install -r requirements.txt

Set the environment variables above before running:

    python main.py

## 📚 Official Supabase guides

- [Access tokens](https://supabase.com/dashboard/account/tokens)
- [List projects API](https://supabase.com/docs/reference/api/v1-list-all-projects)
- [Restore a project API](https://supabase.com/docs/reference/api/v1-restore-a-project)
- [Free project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)

---

Made to be simple. ☀️
