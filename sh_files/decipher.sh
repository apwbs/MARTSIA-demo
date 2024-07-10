#!/bin/sh

requester_name=""
handshake=false
generate_key=false
message_id=""
slice_id=""
output_folder=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    --requester_name|-r)
      requester_name="$2"
      shift # past argument
      shift # past value
      ;;
      -m|--message_id)
      message_id="$2"
      shift # past argument
      shift # past value
      ;;
    -s|--slice_id)
      slice_id="$2"
      shift # past argument
      shift # past value
      ;;
    -o|--output_folder)
      output_folder="$2"
      shift # past argument
      shift # past value
      ;;
    *)
      echo "Unknown option $1"
      exit 1
  esac
done

# Check if requester name is provided
if [ -z "$requester_name" ]; then
  echo "You need to specify --requester_name!"
  exit 1
fi

if [ -z "$message_id" ]; then
  echo "You need to specify --message_id!"
  exit 1
fi

if [ -z "$slice_id" ]; then
  echo "You need to specify --slice_id!"
  exit 1
fi

if [ -n "$output_folder" ] && [ ! -d "$output_folder" ]; then
  echo "Output folder '$output_folder' does not exist"
  exit 1
fi

filename="../src/.env"
count=$(grep -c "AUTHORITY" "$filename")
divided_count=$((count / 3))

# Run the Python script for each authority from 1 to num_authorities
for i in $(seq 1 $divided_count); do
    python3 ../src/client.py --handshake -a "$i" -r "$requester_name"
    echo "✅ Handshake completed for authority $i and requester $requester_name"
    python3 ../src/client.py --generate_key -a "$i" -r "$requester_name"
    echo "✅ Key generation completed for authority $i and requester $requester_name"
done

python3 ../src/reader.py --generate_parameters
echo "✅ Data owner generate parameters done"

matching_lines=$(grep "$slice_id" "../src/.cache")
matching_lines2=$(grep "$message_id" "../src/.cache")

if [ $(echo "$matching_lines" | wc -l) -eq 1 ]; then
  slice_id=$(echo "$matching_lines" | grep -oP '\b\d+\b')
fi

if [ $(echo "$matching_lines2" | wc -l) -eq 1 ]; then
  message_id=$(echo "$matching_lines2" | grep -oP '\b\d+\b')
fi

  python3 ../src/reader.py --access --message_id "$message_id" --slice_id "$slice_id" \
  --reader_name "$requester_name" --output_folder "$output_folder"
  if [ $? -ne 0 ]; then
    echo "Error: python3 command failed."
else
    echo "✅ Data owner access done"
fi

