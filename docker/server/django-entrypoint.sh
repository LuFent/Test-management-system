#!/bin/sh

until cd /app/test-management-system
do
    echo "Waiting for server volume..."
done


until python manage.py makemigrations
do
    echo "Waiting for makemigrations"
    sleep 2
done

until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done


python manage.py init_admin --email=$ADMIN_EMAIL --name=Admin --password=$ADMIN_PASSWORD


python manage.py collectstatic --noinput

gunicorn test_management_system.wsgi --bind 0.0.0.0:8000