#!/bin/bash

# Change directory to where databases are stored
cd ../databases

# Delete and recreate the attribute_certifier database
cd attribute_certifier
rm -f attribute_certifier.db
sqlite3 attribute_certifier.db < ../commands.sql

# Delete and recreate the data_owner database
cd ../data_owner
rm -f data_owner.db
sqlite3 data_owner.db < ../commands.sql

# Delete and recreate the Reader database
cd ../reader
rm -f reader.db
sqlite3 reader.db < ../commands.sql

# Go back to the parent directory
cd ..

# Count the number of Authorities in the .env file
filename="../src/.env"
count=$(grep -c '^[^#]*''NAME="AUTH' "$filename")

# Remove existing Authorities except for authority1
find . -type d -name 'authority*' ! -name 'authority1' -exec rm -rf {} +

# Remove the database for authority1
rm -f "authority1/authority1.db"

# Create copies of authority1 for additional Authorities
for i in $(seq 2 $count); do
    src="authority1"
    dest="authority$i"
    cp -r "$src" "$dest"
done

# Initialize databases for each Authority
for i in $(seq 1 $count); do
    dest="authority$i"
    cd "$dest"
    sqlite3 "$dest.db" < ../commands.sql
    cd ..
done

echo "✅ Database done"

