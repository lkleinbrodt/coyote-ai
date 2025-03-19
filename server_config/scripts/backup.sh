#!/bin/bash

BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# Backup Nginx configuration
tar -czf $BACKUP_DIR/nginx-$DATE.tar.gz /etc/nginx/

# Backup SSL certificates
tar -czf $BACKUP_DIR/letsencrypt-$DATE.tar.gz /etc/letsencrypt/

# Backup application code
tar -czf $BACKUP_DIR/coyote-ai-$DATE.tar.gz /var/www/coyote-ai/

# Remove backups older than 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
