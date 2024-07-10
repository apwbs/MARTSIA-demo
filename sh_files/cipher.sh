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
if [ -n "$input" ] && [ ! -d "$input" ]; then
  echo "Input folder '$input' does not exist"
  exit 1
fi

# Check if policies file exists
if [ -n "$policies" ] && [ ! -f "$policies" ]; then
  echo "Policies file '$policies' does not exist"
  exit 1
fi


python3 ../src/data_owner.py --generate_parameters
echo "✅ Data owner generate parameters done"
python3 ../src/data_owner.py -c -i "$input" -p "$policies" -s "$sender_name"
echo "✅ Data owner cipher done"

