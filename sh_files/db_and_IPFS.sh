#!/bin/bash
# Go to the directory where the databases are stored
cd ../databases

# Create attribute_certifier database
cd attribute_certifier
sqlite3 attribute_certifier.db < ../commands.sql

# Create data_owner database
cd ../data_owner
sqlite3 data_owner.db < ../commands.sql

# Create reader database
cd ../reader
sqlite3 reader.db < ../commands.sql

cd ..

filename="../src/.env"
count=$(grep -c "AUTHORITY" "$filename")
divided_count=$((count / 3))

for i in $(seq 2 $divided_count); do
    src="authority1"
    dest="authority$i"
    cp -r "$src" "$dest"
done

for i in $(seq 1 $divided_count); do
    dest="authority$i"
    cd "$dest"
    sqlite3 "$dest.db" < ../commands.sql
    cd ..
done

echo "✅ Database done!"

ipfs daemon

