#!/bin/bash

# Go to the directory where the databases are stored
cd ../databases

# Delete and recreate the attribute_certifier database
cd attribute_certifier
rm -f attribute_certifier.db
sqlite3 attribute_certifier.db < ../commands.sql

# Delete and recreate the data_owner database
cd ../data_owner
rm -f data_owner.db
sqlite3 data_owner.db < ../commands.sql

# Delete and recreate the reader database
cd ../reader
rm -f reader.db
sqlite3 reader.db < ../commands.sql

cd ..
filename="../src/.env"
count=$(grep -c "AUTHORITY" "$filename")
divided_count=$((count / 3))

find . -type d -name 'authority*' ! -name 'authority1' -exec rm -rf {} +
rm -f "authority1/authority1.db"

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



