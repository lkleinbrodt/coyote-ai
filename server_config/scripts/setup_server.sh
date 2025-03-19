#!/bin/bash

# Exit on any error
set -e

echo "Setting up Coyote AI server configuration..."

# Create application directory if it doesn't exist
sudo mkdir -p /var/www/coyote-ai
sudo chown -R $USER:$USER /var/www/coyote-ai

# Copy Nginx configuration
echo "Setting up Nginx configuration..."
sudo cp nginx/coyote-ai.conf /etc/nginx/sites-available/default
sudo nginx -t
sudo systemctl restart nginx

# Copy systemd service
echo "Setting up systemd service..."
sudo cp systemd/coyote-ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable coyote-ai
sudo systemctl restart coyote-ai

# Copy deployment script
echo "Setting up deployment script..."
cp scripts/deploy.sh /var/www/coyote-ai/
chmod +x /var/www/coyote-ai/deploy.sh

echo "Server configuration complete!"
echo "Remember to:"
echo "1. Set up your .env file using .env.example as a template"
echo "2. Install required packages (Python, Node.js, etc.)"
echo "3. Set up SSL certificates if needed"
