#!/bin/sh

# Read public key of readers
set -e

# Initialize variables
reader=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    --reader)
      reader="$2"
      shift # past argument
      shift # past value
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Check if reader is provided
if [ -z "$reader" ]; then
  echo "Usage: $0 --reader <READER>"
  exit 1
fi

# Run the Python script with the provided arguments
python3 ../src/reader_public_key.py --reader "$reader"
echo "✅ Read public key of $reader"
