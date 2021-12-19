#!/usr/bin/env bash

pip install -r requirements.txt
pip install notion-client
python manage.py collectstatic --no-input
python manage.py migrate