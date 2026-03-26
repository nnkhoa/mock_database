#!/bin/bash
# Start MCP MySQL server + ngrok Tunnel cho Long Châu (lc_aibi)
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

# ── 2. Start MCP server (stdio → HTTP/SSE) trên port 8000 ────────────────────
echo "→ Starting MCP server on port 8000..."
npx supergateway \
    --port 8000 \
    --outputTransport streamableHttp \
    --stdio "env MYSQL_HOST=127.0.0.1 MYSQL_PORT=3306 MYSQL_USER=root MYSQL_PASS=root MYSQL_DB=lc_aibi mcp-server-mysql" \
    > /tmp/mcp_longchau_server.log 2>&1 &
MCP_PID=$!
echo "  MCP PID: $MCP_PID"
sleep 3

# ── 3. Start ngrok tunnel (persistent static domain) ─────────────────────────
source "$SCRIPT_DIR/.env.mcp"
NGROK_DOMAIN="$LONGCHAU_NGROK_DOMAIN"
NGROK_AUTHTOKEN="$LONGCHAU_NGROK_AUTHTOKEN"

echo ""
echo "→ Starting ngrok tunnel..."
ngrok http 8000 --authtoken=$NGROK_AUTHTOKEN --url=$NGROK_DOMAIN --log=stdout > /tmp/ngrok_longchau.log 2>&1 &
NGROK_PID=$!

sleep 4

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Long Châu MCP Server đang chạy!"
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
