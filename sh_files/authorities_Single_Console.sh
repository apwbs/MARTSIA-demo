#!/bin/sh

# Obtain and set the IP address as SERVER_ADDRESS in the .env file
IP_ADDRESS=$(python3 -c "import socket; print(socket.gethostbyname(socket.gethostname()))")
ENV_FILE="../src/.env"
sed -i '/^SERVER_ADDRESS=/d' "$ENV_FILE"
echo "SERVER_ADDRESS=$IP_ADDRESS" >> "$ENV_FILE"

python3 ../src/authorities_single_console.py