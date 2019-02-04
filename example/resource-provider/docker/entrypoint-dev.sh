#!/usr/bin/env sh
set -e

pip install -e ./../django-keycloak/
pip install -e ./../python-keycloak-client/ || true
pip install -e ./../django-dynamic-fixtures/ || true

if [ -f db.sqlite3 ]; then
    echo "Application already initialized."
else
    echo "Initializing application"

    # Run migrations
    python manage.py migrate

    python manage.py load_dynamic_fixtures myapp
fi

if grep -q Yarf /usr/local/lib/python3.7/site-packages/certifi/cacert.pem
    then
        echo "CA already added"
    else
        echo "Add CA to trusted pool"
        echo "\n\n# Yarf" >> /usr/local/lib/python3.7/site-packages/certifi/cacert.pem
        cat /usr/src/ca.pem >> /usr/local/lib/python3.7/site-packages/certifi/cacert.pem
fi

exec "$@"
