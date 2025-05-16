#!/bin/bash

# Ensure the application runs on port 5000 infinitely
nohup python3 main.py --port 5000 > app.log 2>&1 &
echo "Application is running on port 5000. Logs are being written to app.log."
