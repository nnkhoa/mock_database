#!/bin/bash
# Switch MYSQL_DB in supergateway-lc.service and restart
# Usage: sudo bash deploy/mcp-service.sh <customer>
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE="supergateway-lc"
CUSTOMER="${1:-}"

if [ -z "$CUSTOMER" ]; then
  echo "Usage: sudo $0 <customer>"
  echo ""
  echo "Available:"
  for dir in "$PROJECT_DIR"/*_sql/; do
    [ -d "$dir" ] && echo "  $(basename "$dir" | sed 's/_sql$//')"
  done
  exit 1
fi

SQL_DIR="$PROJECT_DIR/${CUSTOMER}_sql"
if [ ! -d "$SQL_DIR" ]; then
  echo "ERROR: Folder '${CUSTOMER}_sql' not found."
  exit 1
fi

DB_NAME=$(grep -m1 '^-- Database:' "$SQL_DIR/01_ddl_schema.sql" | awk '{print $3}')
if [ -z "$DB_NAME" ]; then
  echo "ERROR: Cannot detect database name."
  exit 1
fi

echo "→ Switching to $DB_NAME ..."
sed -i "s/MYSQL_DB=[^ ]*/MYSQL_DB=$DB_NAME/" /etc/systemd/system/${SERVICE}.service
systemctl daemon-reload
systemctl restart ${SERVICE}
echo "✓ Done. MYSQL_DB=$DB_NAME"
