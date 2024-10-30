#!/bin/bash

# Go to the directory where the databases are stored
cd ../databases

# Create attribute_certifier database
cd attribute_certifier
if [ -e "attribute_certifier.db" ]; then
    rm -f attribute_certifier.db  # Remove existing database if it exists
fi
sqlite3 attribute_certifier.db < ../commands.sql  # Create the database from SQL commands

# Create data_owner database
cd ../data_owner
if [ -e "data_owner.db" ]; then
    rm -f data_owner.db  # Remove existing database if it exists
fi
sqlite3 data_owner.db < ../commands.sql  # Create the database from SQL commands

# Create reader database
cd ../reader
if [ -e "reader.db" ]; then
    rm -f reader.db  # Remove existing database if it exists
fi
sqlite3 reader.db < ../commands.sql  # Create the database from SQL commands

cd ..
# Remove all Authority directories except authority1
find . -type d -name 'authority*' ! -name 'authority1' -exec rm -rf {} +

# Remove authority1 database if it exists
if [ -e "authority1/authority1.db" ]; then
    rm -f "authority1/authority1.db"
fi

# Count the number of Authorities in the .env file
filename="../src/.env"
count=$(grep -c '^[^#]*''NAME="AUTH' "$filename")

# Duplicate authority1 directory for each Authority found
for i in $(seq 2 $count); do
    src="authority1"
    dest="authority$i"
    cp -r "$src" "$dest"
done

# Initialize databases for each Authority
for i in $(seq 1 $count); do
    dest="authority$i"
    cd "$dest"
    sqlite3 "$dest.db" < ../commands.sql  # Create the database from SQL commands
    cd ..
done

echo "✅ Database done!"

# Start IPFS daemon
ipfs daemon

