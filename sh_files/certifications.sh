#!/bin/sh

# Initialize variables
input=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    --input|-i)
      input="$2"
      shift # Move to next argument
      shift # Move to next value
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Check if input file argument is provided
if [ -z "$input" ]; then
  echo "Usage: $0 --input <input_file> or $0 -i <input_file>"
  exit 1
fi

# Check if input file exists
if [ ! -f "$input" ]; then
  echo "Input file '$input' does not exist"
  exit 1
fi

# Get lines with ADDRESS, excluding certain keywords
reader_lines=$(grep '^[^#]*'"ADDRESS" ../src/.env | grep -v "AUTHORITY\|CONTRACT\|SERVER\|CERTIFIER" | awk -F"_ADDRESS=" '{print $1}')

echo "$reader_lines" | while IFS= read -r reader; do
    # Read public key for each Authority
    python3 ../src/reader_public_key.py --reader "$reader"
    echo "✅ Read public key of $reader"
done

# Run the attribute certifier script with input file
python3 ../src/attribute_certifier.py -i "$input"
echo "✅ Attribute certifier done"

