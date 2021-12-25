#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
pip install notion-client

python manage.py collectstatic --no-input
python manage.py migrate

echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${DJANGO_ADMIN_USERNAME}', '${DJANGO_ADMIN_EMAIL}', '${DJANGO_ADMIN_PASSWORD}')" | python manage.py shell