#!/bin/sh

# Initialize variables
action=""
input=""
policies=""
sender_name=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    -i|--input)
      input="$2"
      shift # past argument
      shift # past value
      ;;
    -p|--policies)
      policies="$2"
      shift # past argument
      shift # past value
      ;;
    -s|--sender_name)
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

# Check if input folder exists
if [ -z "$input" ] && [ ! -d "$input" ]; then
  echo "You need to provide a directory for the input option: --input"
  exit 1
fi

# Check if policies file exists
if [ -z "$policies" ] && [ ! -f "$policies" ]; then
  echo "You need to provide a file for the policies option: --policies"
  exit 1
fi

# Check if sender_name argument is provided
if [ -z "$sender_name" ]; then
  echo "You need to provide a value for the sender_name parameter: --sender_name"
  exit 1
fi


python3 ../src/data_owner.py --generate_parameters
echo "✅ Data owner generate parameters done"
python3 ../src/data_owner.py -c -i "$input" -p "$policies" -s "$sender_name"
echo "✅ Data owner cipher done"

