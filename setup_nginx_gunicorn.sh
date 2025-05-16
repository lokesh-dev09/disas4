#!/bin/bash

# Update and install necessary packages
sudo apt update
sudo apt install -y nginx python3-pip

# Install Gunicorn
pip3 install gunicorn

# Create Gunicorn systemd service file
sudo bash -c 'cat > /etc/systemd/system/disas4.service <<EOF
[Unit]
Description=Gunicorn instance to serve disas4
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/workspaces/disas4
ExecStart=/usr/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 main:app

[Install]
WantedBy=multi-user.target
EOF'

# Reload systemd and start Gunicorn service
sudo systemctl daemon-reload
sudo systemctl start disas4
sudo systemctl enable disas4

# Create Nginx configuration file
sudo bash -c 'cat > /etc/nginx/sites-available/disas4 <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /workspaces/disas4/static/;
    }

    location /images/ {
        alias /workspaces/disas4/static/images/;
    }
}
EOF'

# Enable Nginx configuration and restart Nginx
sudo ln -s /etc/nginx/sites-available/disas4 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Print success message
echo "Nginx and Gunicorn setup complete. Your website is now live."
