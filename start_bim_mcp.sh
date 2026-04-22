#!/bin/bash
# Start MCP MySQL server + ngrok Tunnel cho BIM Group (bim_realestate_demo)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── 1. Đảm bảo Docker MySQL đang chạy ────────────────────────────────────────
echo "→ Checking MySQL container..."
if ! docker ps --format '{{.Names}}' | grep -q mock_database; then
    echo "  Starting MySQL container..."
    docker start mock_database
    sleep 5
fi
echo "  MySQL OK"

# ── 2. Start MCP server (stdio → HTTP/SSE) trên port 8002 ────────────────────
echo "→ Starting MCP server on port 8002..."
npx supergateway \
    --port 8002 \
    --outputTransport streamableHttp \
    --stdio "env MYSQL_HOST=127.0.0.1 MYSQL_PORT=3306 MYSQL_USER=root MYSQL_PASS=root MYSQL_DB=bim_realestate_demo mcp-server-mysql" \
    > /tmp/mcp_bim_server.log 2>&1 &
MCP_PID=$!
echo "  MCP PID: $MCP_PID"
sleep 3

# ── 3. Start ngrok tunnel (dùng domain/authtoken của TCM) ──────────────────
source "$SCRIPT_DIR/.env.mcp"
NGROK_DOMAIN="$TCM_NGROK_DOMAIN"
NGROK_AUTHTOKEN="$TCM_NGROK_AUTHTOKEN"

echo ""
echo "→ Starting ngrok tunnel..."
ngrok http 8002 --authtoken=$NGROK_AUTHTOKEN --url=$NGROK_DOMAIN --log=stdout > /tmp/ngrok_bim.log 2>&1 &
NGROK_PID=$!

sleep 4

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ BIM Group MCP Server đang chạy!"
echo ""
echo "  URL cố định : https://$NGROK_DOMAIN/mcp"
echo ""
echo "  → Vào Claude.ai > Settings > Integrations > Add Integration"
echo "  → Điền: https://$NGROK_DOMAIN/mcp"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Cleanup khi Ctrl+C
cleanup() {
    echo ""
    echo "→ Stopping..."
    kill $MCP_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
}
trap cleanup EXIT INT TERM

# Giữ script chạy
wait $NGROK_PID
