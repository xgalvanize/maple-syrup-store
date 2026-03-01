#!/bin/bash
set -e

# Check if backup file argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <backup-file.sql.gz>"
  echo "Example: $0 backup-20260228.sql.gz"
  exit 1
fi

BACKUP_FILE="$1"

# Check if file exists
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: Backup file '$BACKUP_FILE' not found"
  exit 1
fi

echo "🔄 Restoring database from: $BACKUP_FILE"
echo "⚠️  This will overwrite existing data!"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Restore cancelled"
  exit 0
fi

echo "📥 Restoring..."
gunzip < "$BACKUP_FILE" | \
  kubectl exec -i deployment/maple-syrup-postgres -- \
  psql -U maple_user maple_store

echo "✅ Database restored successfully!"