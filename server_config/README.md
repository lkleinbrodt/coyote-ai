# Server Configuration Files

This directory contains configuration files for the Coyote AI application deployment.

## Directory Structure
- `nginx/`: Nginx configuration files
- `systemd/`: Systemd service files
- `scripts/`: Deployment and maintenance scripts

## Installation Instructions

### Nginx Configuration
```bash
sudo cp nginx/coyote-ai.conf /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl restart nginx
```

### Systemd Service
```bash
sudo cp systemd/coyote-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart coyote-ai
sudo systemctl enable coyote-ai
```

### Deployment Scripts
```bash
cp scripts/deploy.sh /var/www/coyote-ai/
chmod +x /var/www/coyote-ai/deploy.sh
```

## Environment Variables
Remember to set up the following environment variables in `/var/www/coyote-ai/.env`:
- DATABASE_URL
- SECRET_KEY
- ENV=prod
(Add other required environment variables)
