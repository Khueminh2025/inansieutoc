#!/usr/bin/env bash

echo "Building Tailwind CSS..."
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

# Import service data (nếu chưa có)
# python manage.py import_services || true  # Không crash nếu lỗi
