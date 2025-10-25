#!/bin/bash
# Startup script for CryptoCRM

set -e

echo "=================================="
echo "Starting CryptoCRM..."
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  Warning: backend/.env not found"
    echo "Creating from .env.example..."
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
    echo "⚠️  Please edit backend/.env with your configuration"
    echo ""
fi

# Start services
echo "Starting Docker Compose services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check if database is ready
echo "Checking database connection..."
docker-compose exec -T postgres pg_isready -U cryptocrm || {
    echo "✗ Database is not ready"
    exit 1
}
echo "✓ Database is ready"

# Run migrations
echo ""
echo "Running database migrations..."
docker-compose exec -T backend alembic upgrade head || {
    echo "✗ Migration failed"
    exit 1
}
echo "✓ Migrations completed"

# Initialize database
echo ""
echo "Initializing database with default data..."
docker-compose exec -T backend python init_db.py || {
    echo "⚠️  Warning: Database initialization had issues"
}

echo ""
echo "=================================="
echo "✓ CryptoCRM started successfully!"
echo "=================================="
echo ""
echo "Services:"
echo "  • Frontend:  http://localhost:3000"
echo "  • Backend:   http://localhost:8000"
echo "  • API Docs:  http://localhost:8000/api/v1/docs"
echo "  • Flower:    http://localhost:5555"
echo ""
echo "Default credentials:"
echo "  • Email:     admin@cryptocrm.com"
echo "  • Password:  admin123"
echo ""
echo "⚠️  Remember to change default password!"
echo ""

