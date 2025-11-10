#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# You can add commands here to wait for the database to be ready
# echo "Waiting for postgres..."
# while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
#   sleep 0.1
# done
# echo "PostgreSQL started"

exec "$@"