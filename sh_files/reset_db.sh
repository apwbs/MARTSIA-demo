#!/bin/bash

# Go to the directory where the databases are stored
cd ../databases

# Delete and recreate the attribute_certifier database
cd attribute_certifier
rm -f attribute_certifier.db

# Delete and recreate the data_owner database
cd ../data_owner
rm -f data_owner.db

# Delete and recreate the reader database
cd ../reader
rm -f reader.db

cd ..
filename="../src/.env"
count=$(grep -c "AUTHORITY" "$filename")
divided_count=$((count / 3))

find . -type d -name 'authority*' ! -name 'authority1' -exec rm -rf {} +
rm -f "authority1/authority1.db"

cd ../sh_files

./create_db.sh

