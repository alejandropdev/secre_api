#!/bin/bash
# Railway startup script

echo "🚀 Starting Secre API on Railway..."

# Set default port if not provided
export PORT=${PORT:-8000}

# Run database migrations
echo "📊 Running database migrations..."
python scripts/simple_migrate.py

# Start the application
echo "🌐 Starting FastAPI application on port $PORT..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
