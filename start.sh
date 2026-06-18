#!/usr/bin/env bash
set -euo pipefail

if [ ! -f /app/.env ]; then
  echo "No .env found, generating one from the current environment..."
  cat > /app/.env <<EOF
SECRET_KEY=${SECRET_KEY}
DEBUG=${DEBUG}

DB_ENGINE=${DB_ENGINE}

POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_HOST=${POSTGRES_HOST}
POSTGRES_PORT=${POSTGRES_PORT}

DJANGO_SUPERUSER_USERNAME=${DJANGO_SUPERUSER_USERNAME}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}
DJANGO_SUPERUSER_FIRST_NAME=${DJANGO_SUPERUSER_FIRST_NAME}
DJANGO_SUPERUSER_LAST_NAME=${DJANGO_SUPERUSER_LAST_NAME}
DJANGO_SUPERUSER_PHONE=${DJANGO_SUPERUSER_PHONE}
DJANGO_SUPERUSER_IDENTIFICATION_NUMBER=${DJANGO_SUPERUSER_IDENTIFICATION_NUMBER}
EOF
  echo ".env generated at /app/.env."
fi

if [ "${DB_ENGINE:-}" = "sqlite" ]; then
  echo "DB_ENGINE=sqlite, skipping Postgres wait."
else
  echo "POSTGRES_HOST=${POSTGRES_HOST:-inventory_db} POSTGRES_PORT=${POSTGRES_PORT:-5432} POSTGRES_DB=${POSTGRES_DB:-<unset>} POSTGRES_USER=${POSTGRES_USER:-<unset>}"
  echo "Waiting for database at ${POSTGRES_HOST:-inventory_db}:${POSTGRES_PORT:-5432}..."
  attempt=0
  until python -c "
import os, sys, psycopg2
try:
    psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('POSTGRES_HOST', 'inventory_db'),
        port=os.environ.get('POSTGRES_PORT', '5432'),
    ).close()
except psycopg2.OperationalError as exc:
    print(f'DB not ready yet: {exc}'.strip(), file=sys.stderr)
    sys.exit(1)
"; do
    attempt=$((attempt + 1))
    echo "Attempt ${attempt}: database not reachable yet, retrying in 1s..."
    sleep 1
  done
  echo "Database is up after ${attempt} attempt(s)."
fi

echo "Running migrations..."
python manage.py migrate --noinput
echo "Migrations done."

REQUIRED_SUPERUSER_VARS=(
  DJANGO_SUPERUSER_USERNAME
  DJANGO_SUPERUSER_PASSWORD
  DJANGO_SUPERUSER_EMAIL
  DJANGO_SUPERUSER_FIRST_NAME
  DJANGO_SUPERUSER_LAST_NAME
  DJANGO_SUPERUSER_PHONE
  DJANGO_SUPERUSER_IDENTIFICATION_NUMBER
)
missing_names=()
for var in "${REQUIRED_SUPERUSER_VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    missing_names+=("$var")
  fi
done

if [ "${#missing_names[@]}" -eq 0 ]; then
  echo "All DJANGO_SUPERUSER_* variables are set, checking if superuser already exists..."
  already_exists=$(python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_management_project.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.filter(username=os.environ['DJANGO_SUPERUSER_USERNAME']).exists())
")
  echo "Superuser already exists: ${already_exists}"
  if [ "$already_exists" = "True" ]; then
    echo "Superuser \"${DJANGO_SUPERUSER_USERNAME}\" already exists, skipping."
  else
    echo "Creating superuser \"${DJANGO_SUPERUSER_USERNAME}\"..."
    python manage.py createsuperuser --noinput
    echo "Superuser \"${DJANGO_SUPERUSER_USERNAME}\" created."
  fi
else
  echo "Skipping superuser creation, missing env vars: ${missing_names[*]}"
fi

exec python manage.py runserver 0.0.0.0:8000
