#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py clear_webp_cache --no-input
python manage.py collectstatic --no-input
python manage.py migrate
