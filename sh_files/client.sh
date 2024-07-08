#!/bin/sh

# Initialize variables
num_authorities=""
requester_name=""
handshake=false
generate_key=false

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    --num_authorities|-n)
      num_authorities="$2"
      shift # past argument
      shift # past value
      ;;
    --requester_name|-r)
      requester_name="$2"
      shift # past argument
      shift # past value
      ;;
    --handshake)
      handshake=true
      shift # past argument
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

# Check if number of authorities is provided
if [ -z "$num_authorities" ]; then
  echo "Usage: $0 --num_authorities <number_of_authorities> --requester_name <requester_name> --handshake or --generate_key"
  exit 1
fi

# Check if requester name is provided
if [ -z "$requester_name" ]; then
  echo "Usage: $0 --num_authorities <number_of_authorities> --requester_name <requester_name> --handshake or --generate_key"
  exit 1
fi

# Check if exactly one of --handshake or --generate_key is provided
if [ "$handshake" = true ] && [ "$generate_key" = true ]; then
  echo "Usage: $0 --num_authorities <number_of_authorities> --requester_name <requester_name> --handshake or --generate_key"
  exit 1
elif [ "$handshake" = false ] && [ "$generate_key" = false ]; then
  echo "Usage: $0 --num_authorities <number_of_authorities> --requester_name <requester_name> --handshake or --generate_key"
  exit 1
fi

# Run the Python script for each authority from 1 to num_authorities
for i in $(seq 1 $num_authorities); do
  if [ "$handshake" = true ]; then
    python3 ../src/client.py --handshake -a "$i" -r "$requester_name"
    echo "✅ Handshake completed for authority $i and requester $requester_name"
  elif [ "$generate_key" = true ]; then
    python3 ../src/client.py --generate_key -a "$i" -r "$requester_name"
    echo "✅ Key generation completed for authority $i and requester $requester_name"
  fi
done
