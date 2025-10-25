#!/bin/bash
# Backup script for CryptoCRM database

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
BACKUP_FILE="$BACKUP_DIR/cryptocrm_backup_$DATE.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "=================================="
echo "CryptoCRM Database Backup"
echo "=================================="
echo ""
echo "Backup file: $BACKUP_FILE"
echo ""

# Create backup
echo "Creating backup..."
docker-compose exec -T postgres pg_dump -U cryptocrm cryptocrm | gzip > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✓ Backup created successfully"
    
    # Show backup size
    SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "  Size: $SIZE"
    
    # Remove backups older than 30 days
    echo ""
    echo "Cleaning old backups (older than 30 days)..."
    find $BACKUP_DIR -name "cryptocrm_backup_*.sql.gz" -mtime +30 -delete
    
    # Show remaining backups
    BACKUP_COUNT=$(ls -1 $BACKUP_DIR/cryptocrm_backup_*.sql.gz 2>/dev/null | wc -l)
    echo "✓ Total backups: $BACKUP_COUNT"
else
    echo "✗ Backup failed"
    exit 1
fi

echo ""
echo "=================================="
echo "Backup completed!"
echo "=================================="

