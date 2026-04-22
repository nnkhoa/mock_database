#!/bin/bash
# ==============================================================================
# Install systemd service - Auto-start MCP servers khi EC2 reboot
# Chay: sudo bash deploy/install-service.sh
# ==============================================================================
set -euo pipefail

# Detect user and project path
DEPLOY_USER="${SUDO_USER:-$USER}"
DEPLOY_HOME=$(eval echo "~$DEPLOY_USER")
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# Detect fnm node path
FNM_NODE_DIR="$DEPLOY_HOME/.local/share/fnm/aliases/default/bin"
if [ ! -d "$FNM_NODE_DIR" ]; then
    # Try to find actual fnm node path
    FNM_NODE_DIR=$(find "$DEPLOY_HOME/.local/share/fnm" -name "node" -type f 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo "")
fi

if [ -z "$FNM_NODE_DIR" ]; then
    echo "ERROR: Cannot find fnm Node.js installation!"
    echo "  Run: bash deploy/ec2-setup.sh first"
    exit 1
fi

# Detect npm global bin path
NPM_GLOBAL_BIN=$(su - "$DEPLOY_USER" -c "export PATH=\"$FNM_NODE_DIR:\$PATH\" && npm config get prefix 2>/dev/null")/bin

echo "→ Installing systemd service..."
echo "  User: $DEPLOY_USER"
echo "  Project: $PROJECT_DIR"
echo "  Node dir: $FNM_NODE_DIR"
echo "  npm global bin: $NPM_GLOBAL_BIN"

# Create systemd service file
cat > /etc/systemd/system/mcp-server.service << EOF
[Unit]
Description=MCP MySQL Servers with ngrok tunnels
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=simple
User=$DEPLOY_USER
Group=$DEPLOY_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=/bin/bash $PROJECT_DIR/deploy/deploy.sh
Restart=on-failure
RestartSec=10

# Environment for fnm/node + npm global packages
Environment="PATH=$NPM_GLOBAL_BIN:$FNM_NODE_DIR:/usr/local/bin:/usr/bin:/bin"
Environment="HOME=$DEPLOY_HOME"

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mcp-server

[Install]
WantedBy=multi-user.target
EOF

# Reload and enable
systemctl daemon-reload
systemctl enable mcp-server.service

echo ""
echo "  Service installed!"
echo ""
echo "  Commands:"
echo "    sudo systemctl start mcp-server    # Start"
echo "    sudo systemctl stop mcp-server     # Stop"
echo "    sudo systemctl restart mcp-server  # Restart"
echo "    sudo systemctl status mcp-server   # Status"
echo "    journalctl -u mcp-server -f        # View logs"
echo ""
