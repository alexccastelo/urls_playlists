# YouTube Playlist URL Extractor

Aplicação web para extrair todas as URLs de uma playlist do YouTube e baixar como arquivo `.txt`.

---

## Deploy na VPS (passo a passo)

### 1. Enviar os arquivos para a VPS

```bash
scp -r yt-playlist-extractor/ usuario@ip-da-vps:/var/www/yt-extractor
```

### 2. Acessar a VPS e configurar o ambiente

```bash
ssh usuario@ip-da-vps
cd /var/www/yt-extractor

# Criar ambiente virtual Python
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Testar localmente antes de subir

```bash
source venv/bin/activate
python app.py
# Acesse: http://ip-da-vps:5000
```

### 4. Configurar como serviço (systemd)

```bash
# Copiar o arquivo de serviço
sudo cp yt-extractor.service /etc/systemd/system/

# Ajustar o owner da pasta (se necessário)
sudo chown -R www-data:www-data /var/www/yt-extractor

# Ativar e iniciar o serviço
sudo systemctl daemon-reload
sudo systemctl enable yt-extractor
sudo systemctl start yt-extractor

# Verificar se está rodando
sudo systemctl status yt-extractor
```

### 5. Configurar Nginx como proxy reverso

```bash
# Copiar a config do Nginx
sudo cp nginx.conf /etc/nginx/sites-available/yt-extractor

# Editar com seu domínio ou IP
sudo nano /etc/nginx/sites-available/yt-extractor

# Ativar o site
sudo ln -s /etc/nginx/sites-available/yt-extractor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Pronto! A aplicação estará disponível em `http://seu-dominio.com`.

---

## Estrutura dos arquivos

```
yt-playlist-extractor/
├── app.py                  # Backend Flask
├── templates/
│   └── index.html          # Interface web
├── requirements.txt        # Dependências Python
├── yt-extractor.service    # Serviço systemd
├── nginx.conf              # Configuração Nginx
└── README.md               # Este arquivo
```

---

## Atualizar yt-dlp (recomendado periodicamente)

O YouTube muda com frequência; mantenha o yt-dlp atualizado:

```bash
source /var/www/yt-extractor/venv/bin/activate
pip install -U yt-dlp
sudo systemctl restart yt-extractor
```
