#!/bin/bash
# =============================================================
# webhook.sh — Auto-deploy acionado pelo aaPanel WebHook
# Chamado automaticamente a cada git push no repositório
# =============================================================

APP_DIR="/www/wwwroot/urls_playlists"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="yt-extractor"
LOG_FILE="/var/log/yt-extractor-deploy.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Auto-deploy iniciado ===" >> "$LOG_FILE"

# 1. Atualizar código
cd "$APP_DIR"
git pull origin main >> "$LOG_FILE" 2>&1

# 2. Atualizar dependências (caso requirements.txt tenha mudado)
"$VENV_DIR/bin/pip" install -r requirements.txt -q >> "$LOG_FILE" 2>&1

# 3. Reiniciar o serviço
systemctl restart "$SERVICE_NAME" >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Auto-deploy concluído ===" >> "$LOG_FILE"
