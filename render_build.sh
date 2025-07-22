#!/usr/bin/env bash

# Apply migrations
python manage.py migrate --noinput

# Install Node packages (Tailwind)
npm install

npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
# Collect static files
python manage.py collectstatic --noinput


# Import service data (nếu chưa có)
# python manage.py import_services || true  # Không crash nếu lỗi
