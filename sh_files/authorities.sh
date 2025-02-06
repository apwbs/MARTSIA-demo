#!/bin/bash

# Function to open a terminal and run commands for each Authority
run_commands() {
    local authority=$1
    gnome-terminal -- bash -c "\
        docker exec -it martsia_ethereum_container bash -c ' \
            sleep 0.3 && \
            cd MARTSIA-Demo/sh_files && \
            sleep 0.3 && \
            sh old/authority.sh --authority $authority; \
            sleep 10 && \
            sh old/server_authority.sh --authority $authority; \
            bash' \
        "
}

filename="../src/.env"
# Count Authorities based on NAME="AUTH" lines in the file
count=$(grep -c '^[^#]*''NAME="AUTH' "$filename")
# Run commands for each Authority found
for ((i=1; i<=$count; i++)); do
    run_commands $i
done

# Obtain and set the IP address as SERVER_ADDRESS in the .env file
IP_ADDRESS=$(python3 -c "import socket; print(socket.gethostbyname(socket.gethostname()))")
ENV_FILE="../src/.env"
sed -i '/^SERVER_ADDRESS=/d' "$ENV_FILE"
echo "SERVER_ADDRESS=$IP_ADDRESS" >> "$ENV_FILE"

