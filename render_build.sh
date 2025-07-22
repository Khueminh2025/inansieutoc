#!/usr/bin/env bash

# Apply migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Import service data (nếu chưa có)
python manage.py import_services || true  # Không crash nếu lỗi
