#!/bin/sh

# Initialize variables for input, policies, and sender name
input=""
policies=""
sender_name=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    -i|--input)       # Input directory
      input="$2"
      shift # past argument
      shift # past value
      ;;
    -p|--policies)    # Policies file
      policies="$2"
      shift # past argument
      shift # past value
      ;;
    -s|--sender_name) # Sender name
      sender_name="$2"
      shift # past argument
      shift # past value
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Verify input directory exists
if [ -z "$input" ] && [ ! -d "$input" ]; then
  echo "You need to provide a directory for the input option: --input"
  exit 1
fi

# Verify policies file exists
if [ -z "$policies" ] && [ ! -f "$policies" ]; then
  echo "You need to provide a file for the policies option: --policies"
  exit 1
fi

# Check if sender name argument is provided
if [ -z "$sender_name" ]; then
  echo "You need to provide a value for the sender_name parameter: --sender_name"
  exit 1
fi

# Execute the data owner script with specified arguments
python3 ../src/data_owner.py -i "$input" -p "$policies" -s "$sender_name"
echo "✅ Data owner cipher done"

