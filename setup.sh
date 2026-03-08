#!/bin/bash
# =============================================================
# setup.sh — Deploy inicial na VPS com aaPanel
# Execute UMA VEZ como root após clonar o repositório
# Caminho esperado: /www/wwwroot/urls_playlists/
# =============================================================

set -e  # Para em caso de erro

APP_DIR="/www/wwwroot/urls_playlists"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="yt-extractor"
APP_USER="www"          # usuário padrão do aaPanel
APP_PORT="5000"

echo "======================================"
echo "  Deploy: YouTube Playlist Extractor"
echo "======================================"

# 1. Atualizar código do GitHub
echo "[1/6] Atualizando código do repositório..."
cd "$APP_DIR"
git pull origin main

# 2. Criar ambiente virtual Python
echo "[2/6] Criando ambiente virtual Python..."
python3 -m venv "$VENV_DIR"

# 3. Instalar dependências
echo "[3/6] Instalando dependências..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt" -q

# 4. Criar pasta temporária para arquivos gerados
echo "[4/6] Criando diretório temporário..."
mkdir -p /tmp/yt_extractor
chown -R "$APP_USER":"$APP_USER" /tmp/yt_extractor

# 5. Copiar e ativar o serviço systemd
echo "[5/6] Configurando serviço systemd..."
cp "$APP_DIR/yt-extractor.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

# 6. Verificar status
echo "[6/6] Verificando serviço..."
sleep 2
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "✅ Deploy concluído!"
echo "   App rodando em http://127.0.0.1:$APP_PORT"
echo "   Configure o site no aaPanel apontando para essa porta."
