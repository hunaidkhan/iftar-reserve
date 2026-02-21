# MSA UofA Iftar Auto-Reservation

Automatically reserves your Iftar spot every day at noon MST via GitHub Actions.

---

## How it works

1. `login.py` — run **once** on your Mac to log into Google and save your session
2. `reserve.py` — runs **daily at noon** via GitHub Actions using the saved session
3. Session is stored as a GitHub Secret so Google OAuth is never touched in the cloud

---

## Setup (one time, ~10 minutes)

### Step 1: Install dependencies on your Mac

```bash
pip install playwright
playwright install chromium
```

### Step 2: Run the login script

```bash
python login.py
```

- A Chrome window will open
- Sign in with your `@ualberta.ca` Google account normally
- The script saves your session to `session.json`

### Step 3: Test the reservation script locally

```bash
python reserve.py
```

Make sure it successfully clicks the reserve button before setting up GitHub Actions.

### Step 4: Create a private GitHub repo

Go to github.com → New repository → set it to **Private**.

```bash
git init
git add login.py reserve.py .github/
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

> ⚠️ Do NOT commit `session.json` — it contains your login session. It's already in `.gitignore` below.

### Step 5: Upload your session as a GitHub Secret

1. Open `session.json` and copy its entire contents
2. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `IFTAR_SESSION`
5. Value: paste the contents of `session.json`
6. Click **Add secret**

### Step 6: Push the workflow file

The `.github/workflows/reserve.yml` file is already in your repo. GitHub Actions will automatically pick it up and run daily at noon MST.

You can also trigger it manually anytime via: **Actions tab** → **Daily Iftar Reservation** → **Run workflow**

---

## When the session expires

Supabase sessions typically last 1–4 weeks. When it expires, `reserve.py` will print:

```
ERROR: Session has expired. Please run login.py again to refresh it.
```

You'll also get an email from GitHub Actions saying the workflow failed. Just:

1. Re-run `python login.py` on your Mac
2. Copy the new `session.json` contents
3. Update the `IFTAR_SESSION` secret on GitHub

---

## Files

| File | Purpose |
|------|---------|
| `login.py` | Run once on Mac to save Google session |
| `reserve.py` | Daily reservation script |
| `.github/workflows/reserve.yml` | GitHub Actions cron job |
| `session.json` | Your saved session (⚠️ never commit this) |

---

## .gitignore

Add this to your `.gitignore`:

```
session.json
*.png
__pycache__/
```
