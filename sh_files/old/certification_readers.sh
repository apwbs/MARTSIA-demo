#!/bin/sh

# Read public key of readers
set -e

# Initialize variables
reader=""

reader_lines=$(grep "ADDRESS" ../src/.env | grep -v "AUTHORITY\|CONTRACT\|SERVER\|CERTIFIER" | awk -F"_ADDRESS=" '{print $1}')

echo "$reader_lines" | while IFS= read -r reader; do
    python3 ../src/reader_public_key.py --reader "$reader"
    echo "✅ Read public key of $reader"
done
