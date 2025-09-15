#!/usr/bin/env bash
set -e

echo "Waiting for DB ${POSTGRES_HOST}:${POSTGRES_PORT}..."
python - <<'PY'
import os, time, socket
host = os.getenv("POSTGRES_HOST","db")
port = int(os.getenv("POSTGRES_PORT","5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2): break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit(f"DB {host}:{port} not reachable")
print("DB is up")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python - <<'PY'
import os
from django.core.management import execute_from_command_line
os.environ.setdefault("DJANGO_SETTINGS_MODULE","quiz.settings")
import django; django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username="admin", defaults={"is_staff": True, "is_superuser": True, "email": "admin@example.com"})
if created:
    u.set_password("password")
    u.save()
    print("Created admin/password")
else:
    print("Admin already exists")
PY

python manage.py collectstatic --noinput || true

exec gunicorn quiz.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
