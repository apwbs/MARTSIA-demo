# Default IP and Port
DEFAULT_IP=$(ip route | awk '/default/ {print $3}')
DEFAULT_PORT="7545"
DEFAULT_NETWORK_ID="5777"

# Use provided IP and Port or default to the specified values
IP=${1:-$DEFAULT_IP}
PORT=${2:-$DEFAULT_PORT}
NETWORK_ID=${3:-$DEFAULT_NETWORK_ID}
NEW_URL="http://$IP:$PORT"

# Files to be updated
FILES="../src/client2.py ../src/server_authority.py ../src/block_int.py"
TRUFFLE_CONFIG="../blockchain/truffle-config.js"

# Update the ganache_url in the specified files
for FILE in $FILES; do
    if [ -f "$FILE" ]; then
        sed -i "s#ganache_url = \".*\"#ganache_url = \"$NEW_URL\"#g" "$FILE"
        echo "Updated ganache_url in $FILE"
    else
        echo "File $FILE not found!"
    fi
done

# Update the host and port in truffle-config.js
if [ -f "$TRUFFLE_CONFIG" ]; then
    sed -i "s/host: \".*\".*Localhost/host: \"$IP\",     \/\/ (For Grep) Localhost/g" "$TRUFFLE_CONFIG"
    sed -i "s/port: [0-9]\{4,5\}.*Standard Ethereum/port: $PORT,            \/\/ (For Grep) Standard Ethereum/g" "$TRUFFLE_CONFIG"
    sed -i "s/network_id: [0-9]\{1,5\}.*Any network/network_id: $NETWORK_ID,       \/\/ (For Grep) Any network/g" "$TRUFFLE_CONFIG"
    echo "Updated host, port, and network_id in $TRUFFLE_CONFIG"
else
    echo "File $TRUFFLE_CONFIG not found!"
fi

echo $DEFAULT_IP