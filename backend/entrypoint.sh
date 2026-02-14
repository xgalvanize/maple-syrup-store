#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
	echo '👤 Ensuring Django superuser exists...'
	python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User = get_user_model(); username=os.environ.get('DJANGO_SUPERUSER_USERNAME'); email=os.environ.get('DJANGO_SUPERUSER_EMAIL'); password=os.environ.get('DJANGO_SUPERUSER_PASSWORD');\
user, created = User.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True});\
user.email = email; user.is_staff = True; user.is_superuser = True; user.set_password(password); user.save()"
else
	echo '⚠️  Superuser env vars not set; skipping.'
fi

exec gunicorn syrupstore.wsgi:application --bind 0.0.0.0:8000
