cd ../blockchain
contract_address=$(truffle migrate --network development | tee /dev/tty | grep "> contract address:" | awk '{print $NF}')

# Use sed to replace the value in ../src/.env
sed -i.bak 's/^CONTRACT_ADDRESS_MARTSIA=".*"$/CONTRACT_ADDRESS_MARTSIA="'"$contract_address"'"/' ../src/.env

