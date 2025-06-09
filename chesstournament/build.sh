#!/usr/bin/env bash

export PGUSER="alumnodb"
export PGPASSWORD="alumnodb"

set -o errexit  # exit on error

pip3 install -r requirements.txt

# python manage.py collectstatic --no-input
python manage.py migrate
# python populate_catalog.py || true

python manage.py createsuperuser --username alumnodb --email alumnodb@alumnodb.com --no-input || true

python manage.py shell -c "
# images/management/commands/createsu.py

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.filter(username='alumnodb').first()

if user:
    user.set_password('alumnodb')
    user.save()
else:
    pass
"