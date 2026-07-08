# Riou Ocean Glass — Deployment (production.photo2glass.mu)

## The live server, as it's actually set up
- Code: `/root/phototoglass` (git repo, remote `origin` = the GitHub repo)
- App server: **gunicorn** as a systemd service (`gunicorn.service`), socket at `/run/gunicorn.sock`
- Web server: **nginx**, proxies `/` to gunicorn, serves `/static/` itself from `/var/www/phototoglass/static`
- Database: SQLite at `/root/phototoglass/db.sqlite3` — **contains real orders and content, not demo data**
- Media: `/root/phototoglass/media/` — **contains real uploaded photos/designs**
- `db.sqlite3` and `media/` are **gitignored** — a `git pull` never touches them.

## One-command deploy: `deploy.sh`
After the developer pushes to GitHub, deploy with:
```bash
cd /root/phototoglass
./deploy.sh
```
This single script, every time:
1. **Backs up first, always** — `db.sqlite3` and `media/` to `/root/backups/phototoglass/`
   (timestamped; keeps the newest 10 of each, prunes older ones automatically).
2. Refuses to continue if there are uncommitted local changes, or if `db.sqlite3`/`media/` are
   ever accidentally tracked by git — stops rather than risk overwriting live data.
3. `git pull --ff-only` — updates cleanly, or stops with nothing changed if history ever diverges
   (never auto-merges on production).
4. Installs/updates Python dependencies, runs `migrate`, runs `collectstatic`, syncs the static
   output to nginx's folder, then restarts gunicorn and checks it came back up.

If anything fails partway, the script stops immediately (no half-applied state), and the backup
taken at the very start is always there to restore from.

**Requires `rsync`** (standard on Ubuntu; if missing: `apt-get install -y rsync`, one-time).

## Server-specific settings: `.env` (not in git)
`settings.py` no longer needs hand-editing on the server. `SECRET_KEY`, `DEBUG`, and
`ALLOWED_HOSTS` are read from environment variables, with safe defaults for local dev.
**One-time setup on the server:**
```bash
cd /root/phototoglass
cp .env.example .env
nano .env     # fill in a real SECRET_KEY, DEBUG=False, and your real ALLOWED_HOSTS
```
Then make gunicorn load it too — add this line to `/etc/systemd/system/gunicorn.service`
under `[Service]`:
```
EnvironmentFile=/root/phototoglass/.env
```
then:
```bash
systemctl daemon-reload
systemctl restart gunicorn
```
`deploy.sh` also loads `.env` itself before running `migrate`/`collectstatic`, so manage.py
commands and gunicorn always agree on DEBUG/ALLOWED_HOSTS/SECRET_KEY.

**Important — going from `DEBUG=True` to `DEBUG=False`:** Django currently serves `/media/`
itself only because `DEBUG=True`. Once `DEBUG=False`, add this to the nginx server block
(alongside the existing `/static/` block) before flipping the switch:
```nginx
location /media/ {
    root /root/phototoglass;
}
```
Then `nginx -t && systemctl reload nginx`. Do this in the same session as setting `DEBUG=False`,
not before — otherwise media briefly 404s.

## First-time-only setup on a NEW server (not this one — already done)
```bash
git clone <repo> phototoglass && cd phototoglass
python3 -m venv venv && venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in real values
venv/bin/python manage.py migrate
venv/bin/python manage.py createsuperuser
venv/bin/python manage.py collectstatic --noinput
# (optional, empty DB only) venv/bin/python manage.py seed
```

## What ships via git vs. what's created automatically
- **Code** (templates, views, coded shape outlines, migrations) → git.
- **Fixed studio shapes + sizes** (backgrounds + portraits) → created automatically by
  `migrate` (data migrations `0003`, `0004`). Idempotent — safe to run on a live DB, never
  duplicates, never deletes. Product types (`ptype` → `product_type`) are also safely backfilled
  by migration `0004` rather than reset, so existing live products keep their correct type.
- **Demo content** (placeholder images, sample products) → only via `seed`; not used on production.
- **Real content** (products, collections, logo/favicon, background/portrait assets) → added from
  the dashboard, stored in `media/` on the server (never touched by `git pull`).

## Restoring from a backup (if ever needed)
```bash
systemctl stop gunicorn
cp /root/backups/phototoglass/db-<timestamp>.sqlite3 /root/phototoglass/db.sqlite3
tar -xzf /root/backups/phototoglass/media-<timestamp>.tar.gz -C /root/phototoglass/
systemctl start gunicorn
```
