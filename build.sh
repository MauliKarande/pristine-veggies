#!/usr/bin/env bash

pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput

if [ "$CREATE_SUPERUSER" = "true" ]; then
  python manage.py createsuperuser --noinput || true
fi
