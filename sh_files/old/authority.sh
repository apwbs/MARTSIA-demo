#!/bin/sh

# Initialize variables
authority=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    --authority|-a)
      authority="$2"
      shift # past argument
      shift # past value
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Check if authority number is provided
if [ -z "$authority" ]; then
  echo "Usage: $0 --authority <authority_number>"
  exit 1
fi

# Run the Python script with the provided authority number
python3 ../src/authority.py -a "$authority"
echo "✅ Authority script completed"
