#!/bin/bash
# Start tất cả MCP servers (không dùng ngrok — dùng với Nginx reverse proxy)
set -e

BASE_URL="https://ai4bimcp.ubntddns.com"

# ── 1. Đảm bảo Docker MySQL đang chạy ────────────────────────────────────────
echo "→ Checking MySQL container..."
if ! docker ps --format '{{.Names}}' | grep -q mock_database; then
    echo "  Starting MySQL container..."
    docker start mock_database
    sleep 5
fi
echo "  MySQL OK"

# ── 2. Định nghĩa danh sách MCP servers ──────────────────────────────────────
# Thêm database mới: thêm 1 dòng theo format "PORT|DB_NAME|PATH"
SERVERS=(
    "8000|lc_aibi|longchau"
    "8001|textile_tcm_demo|tcm"
)

# ── 3. Start từng MCP server ──────────────────────────────────────────────────
PIDS=()

for entry in "${SERVERS[@]}"; do
    PORT=$(echo $entry | cut -d'|' -f1)
    DB=$(echo $entry | cut -d'|' -f2)
    PATH_NAME=$(echo $entry | cut -d'|' -f3)

    echo "→ Starting MCP server: $DB on port $PORT..."
    npx supergateway \
        --port $PORT \
        --outputTransport streamableHttp \
        --stdio "env MYSQL_HOST=127.0.0.1 MYSQL_PORT=3306 MYSQL_USER=root MYSQL_PASS=root MYSQL_DB=$DB mcp-server-mysql" \
        > /tmp/mcp_${PATH_NAME}_server.log 2>&1 &

    PIDS+=($!)
    echo "  PID: ${PIDS[-1]}"
done

sleep 3

# ── 4. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Tất cả MCP servers đang chạy!"
echo ""
for entry in "${SERVERS[@]}"; do
    PATH_NAME=$(echo $entry | cut -d'|' -f3)
    echo "  $BASE_URL/$PATH_NAME"
done
echo ""
echo "  → Vào Claude.ai > Settings > Integrations > Add Integration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── 5. Cleanup khi Ctrl+C ─────────────────────────────────────────────────────
cleanup() {
    echo ""
    echo "→ Stopping all MCP servers..."
    for PID in "${PIDS[@]}"; do
        kill $PID 2>/dev/null
    done
}
trap cleanup EXIT INT TERM

wait
