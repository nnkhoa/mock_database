#!/bin/bash
# Populate demo data from <customer>_sql folder into Docker MySQL
# Usage: ./populate.sh <customer_name>
#   e.g. ./populate.sh ptscmc
#        ./populate.sh trasas

CONTAINER="mock_database"
MYSQL_USER="root"
MYSQL_PASS="root"

if [ -z "$1" ]; then
  echo "Usage: ./populate.sh <customer_name>"
  echo ""
  echo "Available datasets:"
  for dir in *_sql/; do
    [ -d "$dir" ] && echo "  ${dir%_sql/}"
  done
  exit 1
fi

SQL_DIR="${1}_sql"

if [ ! -d "$SQL_DIR" ]; then
  echo "ERROR: Folder '$SQL_DIR' not found."
  echo ""
  echo "Available datasets:"
  for dir in *_sql/; do
    [ -d "$dir" ] && echo "  ${dir%_sql/}"
  done
  exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  echo "ERROR: Container '$CONTAINER' is not running."
  exit 1
fi

DB_NAME=$(grep -m1 '^-- Database:' "$SQL_DIR/01_ddl_schema.sql" | awk '{print $3}')

if [ -z "$DB_NAME" ]; then
  echo "ERROR: Cannot detect database name from $SQL_DIR/01_ddl_schema.sql"
  exit 1
fi

echo "Resetting database '$DB_NAME' ..."
docker exec -i "$CONTAINER" mysql -u"$MYSQL_USER" -p"$MYSQL_PASS" \
  -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null

if [ $? -ne 0 ]; then
  echo "ERROR: Failed to reset database '$DB_NAME'"
  exit 1
fi

echo "Populating from $SQL_DIR ..."

for sql_file in "$SQL_DIR"/0[1-4]*.sql; do
  [ ! -f "$sql_file" ] && continue
  filename=$(basename "$sql_file")
  docker exec -i "$CONTAINER" mysql -u"$MYSQL_USER" -p"$MYSQL_PASS" < "$sql_file" 2>/dev/null
  if [ $? -eq 0 ]; then
    echo "  ✓ $filename"
  else
    echo "  ✗ $filename FAILED"
    exit 1
  fi
done

echo "Done."
