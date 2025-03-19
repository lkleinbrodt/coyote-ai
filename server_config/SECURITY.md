# Security Configuration Guide

## Overview
This document explains the security measures implemented on our VPS server. Each measure serves a specific purpose in protecting our application.

## Key Components

### 1. Firewall (UFW)
- **What**: A firewall that controls incoming/outgoing traffic
- **Why**: Prevents unauthorized access to our server
- **Key Points**:
  - Only allows SSH (port 22), HTTP (80), and HTTPS (443)
  - All other incoming traffic is blocked
  - Located in: `security/ufw_config`

### 2. SSL/HTTPS (Certbot)
- **What**: Encrypts traffic between users and our server
- **Why**: Prevents data interception and adds legitimacy
- **Key Points**:
  - Free certificates from Let's Encrypt
  - Auto-renews every 90 days
  - Configuration in Nginx config

### 3. Fail2ban
- **What**: Intrusion prevention system
- **Why**: Blocks malicious attempts to access our server
- **Key Points**:
  - Blocks IPs after failed login attempts
  - Protects SSH and Nginx
  - Config in: `fail2ban/jail.local`

### 4. Rate Limiting
- **What**: Limits how many requests a user can make
- **Why**: Prevents abuse and DDoS attacks
- **Key Points**:
  - Different limits for API vs regular traffic
  - Configuration in Nginx config

### 5. Security Monitoring
- **What**: Daily security checks and reports
- **Why**: Helps identify issues early
- **Key Points**:
  - Checks system resources
  - Monitors failed login attempts
  - Reports suspicious activity
  - Scripts in: `scripts/security_check.sh`

### 6. Automatic Updates
- **What**: Keeps system packages updated
- **Why**: Ensures we have latest security patches
- **Key Points**:
  - Updates run automatically
  - Configured via unattended-upgrades

### 7. Backups
- **What**: Daily backups of critical configurations
- **Why**: Allows recovery from failures or breaches
- **Key Points**:
  - Backs up Nginx, SSL certs, and application code
  - Rotates backups every 7 days
  - Script in: `scripts/backup.sh`

## Common Tasks

### Checking System Status
```bash
# View firewall status
sudo ufw status

# Check fail2ban status
sudo fail2ban-client status

# View security logs
sudo tail -f /var/log/auth.log

# Check SSL certificates
sudo certbot certificates
```

### After Configuration Changes
```bash
# Test Nginx config
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Restart fail2ban
sudo systemctl restart fail2ban
```

## Emergency Contacts
- SSL Issues: https://letsencrypt.org/docs/
- Security Incidents: Create incident report in GitHub issues
