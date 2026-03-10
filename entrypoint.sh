#!/bin/sh

# Xatolik bo'lsa to'xtash
set -e

echo "PostgreSQL bazasini kutish ($DB_HOST:$DB_PORT)..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL tayyor!"

echo "Migratsiyalarni amalga oshirish..."
python manage.py migrate --noinput

echo "Statik fayllarni yig'ish..."
python manage.py collectstatic --noinput

echo "Gunicorn ishga tushmoqda..."
exec gunicorn techblog.wsgi:application --bind 0.0.0.0:8000