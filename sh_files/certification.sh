#!/bin/sh

# Initialize variables
input=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    --input|-i)
      input="$2"
      shift # past argument
      shift # past value
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

# Run the Python script with the provided arguments
python3 ../src/attribute_certifier.py -i "$input"
echo "✅ Attribute certifier done"