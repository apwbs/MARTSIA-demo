#!/bin/bash

run_commands() {
    local authority=$1
    gnome-terminal -- bash -c "\
        docker exec -it martsia_ethereum_container bash -c ' \
            sleep 0.3 && \
            cd MARTSIA-demo/sh_files && \
            sleep 0.3 && \
            sh old/authority.sh --authority $authority; \
            sleep 10 && \
            sh old/server_authority.sh --authority $authority; \
            bash' \
        "
}
filename="../src/.env"
count=$(grep -c "AUTHORITY" "$filename")
divided_count=$((count / 3))
for ((i=1; i<=$divided_count; i++)); do
    run_commands $i
done

IP_ADDRESS=$(python3 -c "import socket; print(socket.gethostbyname(socket.gethostname()))")
ENV_FILE="../src/.env"
sed -i '/^SERVER_ADDRESS=/d' "$ENV_FILE"
echo "SERVER_ADDRESS=$IP_ADDRESS" >> "$ENV_FILE"







