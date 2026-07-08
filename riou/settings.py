import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# These three are the only values that ever differ between local dev and the live
# server. They now come from environment variables (set in systemd's EnvironmentFile
# on the server, e.g. /root/phototoglass/.env) so this settings.py file itself never
# needs server-specific hand-edits — `git pull` on the server stays conflict-free.
# Locally, sensible dev defaults are used automatically if the env vars aren't set.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me-in-production")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "riou.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "store.context_processors.site",
    ]},
}]

WSGI_APPLICATION = "riou.wsgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Indian/Mauritius"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Studio sends a high-resolution design image with the order; allow a generous body size.
DATA_UPLOAD_MAX_MEMORY_SIZE = 64 * 1024 * 1024   # 64 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 64 * 1024 * 1024
