#!/bin/bash

# Change directory to the blockchain folder
cd ../blockchain

# Migrate contracts and capture the contract address
contract_address=$(truffle migrate --network development | tee /dev/tty | grep "> contract address:" | awk '{print $NF}')

# Use sed to replace the CONTRACT_ADDRESS_MARTSIA in the .env file
sed -i.bak 's/^CONTRACT_ADDRESS_MARTSIA=".*"$/CONTRACT_ADDRESS_MARTSIA="'"$contract_address"'"/' ../src/.env
