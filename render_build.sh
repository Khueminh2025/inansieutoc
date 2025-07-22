#!/usr/bin/env bash

# Apply migrations
python manage.py migrate --noinput

# Install Node packages (Tailwind)
npm install

npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/output.css --watch
# Collect static files
python manage.py collectstatic --noinput


# Import service data (nếu chưa có)
# python manage.py import_services || true  # Không crash nếu lỗi
