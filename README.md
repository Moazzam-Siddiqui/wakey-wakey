# Wakey Wakey ☀️

**A tiny helper that checks your Supabase projects automatically.**

Wakey Wakey runs on GitHub Actions. Every 6 hours it looks at the Supabase projects your access token can see.

It can:
- Notice when a project is inactive.
- Ask Supabase to restore an inactive project.
- Run a safe, read-only database check (SELECT 1) when you add a database password.
- Show a report in GitHub Actions.

Your computer does not need to be on.

> This is a helper, not a guarantee. Supabase decides when projects pause. A restore request may take time. An accepted request does not prove the project is awake yet.

---

## 🚀 Install it in your GitHub account

### Step 1 — Copy this project

1. Open this page.
2. Click **Fork**.
3. Open your new copy.

A fork is your own copy of Wakey Wakey.

### Step 2 — Make a Supabase key

1. Sign in to [Supabase](https://supabase.com/dashboard).
2. Open your account settings.
3. Open **Access Tokens**.
4. Create a Personal Access Token.
5. Give it permission to read your project list. Also give it permission to restore projects if you want automatic restoring.
6. Copy the token. Keep it secret!

### Step 3 — Put the key in GitHub

1. Open your GitHub fork.
2. Click **Settings**.
3. Click **Secrets and variables → Actions**.
4. Under **Secrets**, click **New repository secret**.
5. Name: SUPABASE_ACCESS_TOKEN
6. Value: paste your Supabase token.
7. Save it.

Never put this key in a code file or public message.

### Step 4 — Projects are included automatically

By default, Wakey Wakey checks **every project** your token can see. New projects are included automatically. You do not need to update a project list when you create another Supabase project.

Want Wakey Wakey to leave a project alone?

1. Find that project's Supabase **Reference ID**.
2. Open GitHub **Settings → Secrets and variables → Actions → Variables**.
3. Add a variable named SUPABASE_EXCLUDED_PROJECT_REFS.
4. Put the project refs to skip, separated by commas.

This repository starts with the Agentic Workflow project excluded. Wakey Wakey leaves it alone. All other current and future projects are included automatically.

If you fork this repository, replace that example exclusion with a project ref in your own Supabase account, or remove the variable if you want every project included.

### Step 5 — (Optional) Add database passwords

This enables the extra database connection check.

1. Open your Supabase project.
2. Go to **Project Settings → Database**.
3. Find your database password.
4. In GitHub, open **Settings → Secrets and variables → Actions → Secrets**.
5. Add a secret named SUPABASE_DB_PASSWORDS.
6. Its value must be JSON. Example:

    {
      "your_project_ref": "your_database_password"
    }

Add more project refs and passwords inside the same JSON object if needed.

You can also add SUPABASE_DB_HOSTS as another secret if you need custom hostnames. The database check only runs SELECT 1. It does not edit your data.

### Step 6 — Switch it on

1. Open the **Actions** tab in your GitHub fork.
2. Enable workflows if GitHub asks.
3. Select **Wakey Wakey**.
4. Click **Run workflow**.

Done! It will also run automatically every 6 hours. GitHub may delay scheduled runs when its servers are busy.

---

## 🧸 What do the words mean?

| Word | Meaning |
|---|---|
| ACTIVE_HEALTHY | Supabase says the project is active. |
| INACTIVE | Supabase says the project is inactive. |
| restore=requested | Wakey Wakey asked Supabase to restore it. |
| database=ok | The small database check worked. |
| database=not_configured | No database password was added for this project. |
| database=failed | The database check could not connect. |

To see the report: open **Actions → Wakey Wakey → latest run → Summary**.

## ⚙️ All settings

| Name | Type | Needed? | What it does |
|---|---|---|---|
| SUPABASE_ACCESS_TOKEN | Secret | Yes | Lets Wakey Wakey see your projects. |
| SUPABASE_EXCLUDED_PROJECT_REFS | Variable | No | Projects to skip. Empty means skip none. |
| SUPABASE_DB_PASSWORDS | Secret | No | Turns on database checks. |
| SUPABASE_DB_HOSTS | Secret | No | Custom database hostnames. |
| SUPABASE_DB_PORT | Variable | No | Database port. Default: 5432. |

Automatic restore requests are turned on in the workflow. To turn them off, edit .github/workflows/wakey-wakey.yml and change RESTORE_INACTIVE_PROJECTS from true to false.

## ❓ Help! It is not working.

- **No projects found:** Check your SUPABASE_ACCESS_TOKEN secret and its project-list permission.
- **Restore failed:** Check that your token can restore projects. Read the error in the Actions log.
- **Database not configured:** Add the password secret described above.
- **Database check failed:** Check the password and hostname.
- **No automatic run:** Check that GitHub Actions is enabled.

## 🔐 Keep your keys safe

- Never share your Supabase token or database password.
- Save private values only in GitHub Actions Secrets.
- Do not commit secrets to Git.
- Database checks use only SELECT 1.

## 💻 Run it on your own computer

You need Python 3.11 or newer.

    python -m pip install -r requirements.txt
    python main.py

Set the environment variables above before running the program.

## 📖 Official Supabase help

- [Access tokens](https://supabase.com/dashboard/account/tokens)
- [List projects API](https://supabase.com/docs/reference/api/v1-list-all-projects)
- [Restore a project API](https://supabase.com/docs/reference/api/v1-restore-a-project)
- [Free project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)

---

Made to be simple. ☀️
