#!/bin/bash

# Exit on error
set -e

echo "Setting up security configurations..."

# Install required packages
sudo apt update
sudo apt install -y ufw fail2ban unattended-upgrades mailutils

# Set up UFW
bash security/ufw_config

# Set up fail2ban
sudo cp fail2ban/jail.local /etc/fail2ban/jail.local
sudo systemctl restart fail2ban

# Set up security check script
sudo cp scripts/security_check.sh /root/
sudo chmod +x /root/security_check.sh

# Set up backup script
sudo cp scripts/backup.sh /root/
sudo chmod +x /root/backup.sh

# Set up automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades

echo "Security configuration complete!"
echo "Remember to:"
echo "1. Set up email in /etc/aliases for root mail"
echo "2. Add security check and backup scripts to crontab"
echo "3. Review and customize rate limits in Nginx configuration"
