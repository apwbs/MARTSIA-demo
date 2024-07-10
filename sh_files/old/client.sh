#!/bin/sh

requester_name=""
generate_key=false

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    --requester_name|-r)
      requester_name="$2"
      shift # past argument
      shift # past value
      ;;
    --generate_key)
      generate_key=true
      shift # past argument
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Check if requester name is provided
if [ -z "$requester_name" ]; then
  echo "You need to specify --requester_name!"
  exit 1
fi

filename="../src/.env"
count=$(grep -c "AUTHORITY" "$filename")
divided_count=$((count / 3))

# Run the Python script for each authority from 1 to num_authorities
for i in $(seq 1 $divided_count); do
  if [ "$generate_key" = true ]; then
    python3 ../src/client.py --handshake -a "$i" -r "$requester_name"
    echo "✅ Handshake completed for authority $i and requester $requester_name"
    python3 ../src/client.py --generate_key -a "$i" -r "$requester_name"
    echo "✅ Key generation completed for authority $i and requester $requester_name"
  fi
done
