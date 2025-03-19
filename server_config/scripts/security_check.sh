#!/bin/bash

echo "Security Check Report - $(date)"
echo "=============================="

echo -e "\nDisk Usage:"
df -h

echo -e "\nMemory Usage:"
free -h

echo -e "\nCPU Load:"
uptime

echo -e "\nActive SSH Sessions:"
who

echo -e "\nFailed SSH Attempts (last 24h):"
grep "Failed password" /var/log/auth.log | tail -n 10

echo -e "\nBanned IPs (fail2ban):"
sudo fail2ban-client status

echo -e "\nLast 10 UFW Blocks:"
sudo grep "UFW BLOCK" /var/log/ufw.log | tail -n 10

echo -e "\nNginx Error Log (last 10 entries):"
tail -n 10 /var/log/nginx/error.log

echo -e "\nSSL Certificate Status:"
sudo certbot certificates

echo -e "\nSystem Updates Available:"
sudo apt update > /dev/null
sudo apt list --upgradable
