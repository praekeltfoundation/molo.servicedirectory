#!/bin/bash

cd testapp
set -e

./manage.py migrate --noinput
./manage.py collectstatic --noinput

echo "from django.contrib.auth.models import User
if not User.objects.filter(username='admin').count():
    User.objects.create_superuser('admin', 'admin@example.com', 'tempadminpass')
" | ./manage.py shell

echo "=> Starting nginx"
nginx; service nginx reload

echo "=> Starting Supervisord"
supervisord -c /etc/supervisord.conf

echo "=> Tailing logs"
tail -qF /var/log/supervisor/*.log
