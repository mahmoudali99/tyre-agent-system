#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "import psycopg2; psycopg2.connect('$DATABASE_URL_SYNC')" 2>/dev/null; do
    sleep 2
done
echo "PostgreSQL ready."

echo "Running seed..."
python -m backend.seed || echo "Seed completed (or already seeded)"

echo "Starting server..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
