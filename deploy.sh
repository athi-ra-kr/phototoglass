#!/usr/bin/env bash
# Riou Ocean Glass — one-command deploy.
# Run this ON THE SERVER, from the project folder, every time after the developer
# has pushed to GitHub:
#
#   cd /root/phototoglass && ./deploy.sh
#
# It always backs up the live database + media BEFORE touching anything, then
# pulls the new code, applies migrations, refreshes static files, and restarts
# gunicorn. It stops immediately (set -e) on the first error, so a failed step
# never leaves things half-updated.

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATIC_TARGET="/var/www/phototoglass/static"     # served by nginx — adjust if it ever moves
BACKUP_DIR="/root/backups/phototoglass"
KEEP_BACKUPS=10                                   # prune older backups beyond this count
STAMP="$(date +%Y%m%d-%H%M%S)"

cd "$PROJECT_DIR"
echo "== Riou Ocean Glass deploy — $STAMP =="

# ---------- 0. load server-specific settings (SECRET_KEY / DEBUG / ALLOWED_HOSTS) ----------
if [ -f ".env" ]; then
  set -a; source .env; set +a
else
  echo "!! No .env found — DEBUG/ALLOWED_HOSTS/SECRET_KEY will fall back to dev defaults."
  echo "!! Copy .env.example to .env and fill in real values before going further."
fi

# ---------- 1. backup FIRST, always ----------
mkdir -p "$BACKUP_DIR"
if [ -f "db.sqlite3" ]; then
  cp db.sqlite3 "$BACKUP_DIR/db-$STAMP.sqlite3"
  echo "-> DB backed up to $BACKUP_DIR/db-$STAMP.sqlite3"
fi
if [ -d "media" ]; then
  tar -czf "$BACKUP_DIR/media-$STAMP.tar.gz" media
  echo "-> media/ backed up to $BACKUP_DIR/media-$STAMP.tar.gz"
fi
# keep only the newest $KEEP_BACKUPS of each kind
cd "$BACKUP_DIR"
ls -1t db-*.sqlite3 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm -f
ls -1t media-*.tar.gz 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm -f
cd "$PROJECT_DIR"

# ---------- 2. refuse to pull over uncommitted local changes ----------
if [ -n "$(git status --porcelain)" ]; then
  echo "!! There are uncommitted local changes in $PROJECT_DIR — aborting so nothing is lost."
  git status --short
  exit 1
fi

# ---------- 2b. make sure the live DB/media were never committed to git ----------
if git ls-files | grep -qE '^db\.sqlite3$|^media/'; then
  echo "!! db.sqlite3 or media/ is tracked by git — a pull could overwrite live data."
  echo "!! Fix once with: git rm -r --cached db.sqlite3 media && git commit -m 'stop tracking db/media'"
  echo "!! (your backups above are safe either way, but stopping here rather than risk a pull.)"
  exit 1
fi

# ---------- 3. pull the new code (fast-forward only — never auto-merge on prod) ----------
echo "-> git pull --ff-only"
if ! git pull --ff-only; then
  echo "!! git pull did not fast-forward cleanly (diverged history?). Nothing was changed."
  echo "!! Investigate manually with: git status / git log --oneline --all -10"
  exit 1
fi

# ---------- 4. dependencies ----------
echo "-> installing/updating dependencies"
venv/bin/pip install -q -r requirements.txt

# ---------- 5. migrate (DB is already backed up above) ----------
echo "-> migrate"
venv/bin/python manage.py migrate --noinput

# ---------- 6. static files ----------
echo "-> collectstatic"
venv/bin/python manage.py collectstatic --noinput -v 0
mkdir -p "$STATIC_TARGET"
rsync -a --delete staticfiles/ "$STATIC_TARGET/"
chown -R www-data:www-data "$STATIC_TARGET"

# ---------- 7. restart the app ----------
echo "-> restarting gunicorn"
systemctl restart gunicorn
sleep 1
systemctl is-active --quiet gunicorn && echo "-> gunicorn is running" || { echo "!! gunicorn failed to start — check: journalctl -u gunicorn -n 50"; exit 1; }

echo "== Deploy complete ($STAMP) =="
echo "Backups kept in $BACKUP_DIR (latest $KEEP_BACKUPS of each)."
