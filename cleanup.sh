#!/bin/bash

# Set working directory
cd /var/www/coyote-ai

# Clear Python cache files
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Clear old log files (older than 7 days)
find . -type f -name "*.log" -mtime +7 -delete

# Clear temporary files
rm -rf /tmp/coyote-ai-*

# Check memory usage
MEMORY_USAGE=$(free -m | awk '/Mem:/ {print $3/$2 * 100.0}')
if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
    echo "High memory usage detected ($MEMORY_USAGE%). Restarting application..."
    systemctl restart coyote-ai
fi

# Clear old session files
find ./flask_session -type f -mtime +7 -delete

# Clear old database backups (if any)
find . -type f -name "*.sql" -mtime +7 -delete

# Log cleanup completion
echo "Cleanup completed at $(date)" >> /var/log/coyote-ai-cleanup.log 