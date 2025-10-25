#!/bin/bash
# Restore script for CryptoCRM database

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available backups:"
    ls -1t backups/cryptocrm_backup_*.sql.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "✗ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=================================="
echo "CryptoCRM Database Restore"
echo "=================================="
echo ""
echo "⚠️  WARNING: This will overwrite the current database!"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo ""
echo "Stopping application services..."
docker-compose stop backend celery_worker celery_beat

echo ""
echo "Restoring database..."
gunzip -c $BACKUP_FILE | docker-compose exec -T postgres psql -U cryptocrm cryptocrm

if [ $? -eq 0 ]; then
    echo "✓ Database restored successfully"
else
    echo "✗ Restore failed"
    exit 1
fi

echo ""
echo "Starting application services..."
docker-compose start backend celery_worker celery_beat

echo ""
echo "=================================="
echo "Restore completed!"
echo "=================================="

