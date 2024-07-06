# Go to the directory where the databases are stored
cd ../databases

# Create attribute_certifier database
cd attribute_certifier
sqlite3 attribute_certifier.db < ../commands.sql
echo "attribute_certifier.db created (1/7)"

# Create data_owner database
cd ../data_owner
sqlite3 data_owner.db < ../commands.sql
echo "data_owner.db created (2/7)"

# Create reader database
cd ../reader
sqlite3 reader.db < ../commands.sql
echo "reader.db created (3/7)"

# Create authority1 database
cd ../authority1
sqlite3 authority1.db < ../commands.sql
echo "authority1.db created (4/7)"

# Create authority2 database
cd ../authority2
sqlite3 authority2.db < ../commands.sql
echo "authority2.db created (5/7)"

# Create authority3 database
cd ../authority3
sqlite3 authority3.db < ../commands.sql
echo "authority3.db created (6/7)"

# Create authority4 database
cd ../authority4
sqlite3 authority4.db < ../commands.sql
echo "authority4.db created (7/7)"