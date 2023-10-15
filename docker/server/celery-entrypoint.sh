#!/bin/sh

until cd /app/test-management-system
do
    echo "Waiting for server volume..."
done

celery -A test_management_system worker --loglevel=info --concurrency 1 -E
