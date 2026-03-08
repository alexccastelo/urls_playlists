# YouTube Playlist URL Extractor

Extrai todas as URLs de uma playlist pública do YouTube e disponibiliza para download em `.txt`.

---

## Estrutura do projeto

```
urls_playlists/
├── app.py                  # Backend Flask
├── templates/
│   └── index.html          # Interface web
├── requirements.txt        # Dependências Python
├── yt-extractor.service    # Serviço systemd (produção)
├── nginx.conf              # Referência de config do Nginx
├── setup.sh                # Script de deploy inicial
├── webhook.sh              # Script de auto-deploy (GitHub → aaPanel)
└── README.md
```

---

## Deploy na VPS com aaPanel (passo a passo)

### PARTE 1 — Configurar o site no aaPanel

1. No aaPanel, acesse **Website → Add site**
2. Preencha:
   - **Domain:** seu domínio ou IP da VPS
   - **Root directory:** `/www/wwwroot/urls_playlists`
   - **PHP version:** selecione **Pure Static** (não usamos PHP)
3. Clique em **Confirm**

---

### PARTE 2 — Deploy inicial (via SSH)

```bash
# Acesse a VPS
ssh root@ip-da-vps

# Entre no diretório do projeto (já clonado)
cd /www/wwwroot/urls_playlists

# Dê permissão e execute o script de setup
chmod +x setup.sh webhook.sh
bash setup.sh
```

O script faz automaticamente:
- `git pull` do repositório
- Criação do virtualenv Python em `./venv/`
- Instalação das dependências (`flask`, `yt-dlp`, `gunicorn`)
- Ativação do serviço `yt-extractor` via systemd

---

### PARTE 3 — Configurar Nginx no aaPanel

1. No aaPanel, vá em **Website → clique no site → Config**
2. Clique em **Nginx Config** e substitua o bloco `server {}` pelo conteúdo do arquivo `nginx.conf` deste projeto (ajuste o `server_name` para seu domínio/IP)
3. Clique em **Save**

---

### PARTE 4 — Auto-deploy com GitHub Webhook

1. No aaPanel, vá em **WebHook → Add**
2. Preencha:
   - **Name:** `yt-extractor-deploy`
   - **Script path:** `/www/wwwroot/urls_playlists/webhook.sh`
3. Copie a **URL do webhook** gerada pelo aaPanel
4. No GitHub, acesse o repositório → **Settings → Webhooks → Add webhook**
5. Preencha:
   - **Payload URL:** cole a URL do aaPanel
   - **Content type:** `application/json`
   - **Events:** selecione **Just the push event**
6. Clique em **Add webhook**

A partir de agora, cada `git push` acionará o `webhook.sh` automaticamente.

---

### PARTE 5 — Firewall

| Porta | Situação       | Observação                                      |
|-------|----------------|-------------------------------------------------|
| 80    | Deve estar aberta | Nginx já usa — verificar em aaPanel Security |
| 443   | Opcional       | Recomendado — aaPanel tem Let's Encrypt nativo  |
| 5000  | **NÃO abrir**  | Flask roda apenas em 127.0.0.1 (interno)        |

Não é necessário abrir nenhuma porta nova se a 80 já estiver liberada.

---

## Comandos úteis

```bash
# Ver status do serviço
systemctl status yt-extractor

# Reiniciar manualmente
systemctl restart yt-extractor

# Ver logs em tempo real
journalctl -u yt-extractor -f

# Atualizar yt-dlp (fazer periodicamente)
/www/wwwroot/urls_playlists/venv/bin/pip install -U yt-dlp
systemctl restart yt-extractor
```
