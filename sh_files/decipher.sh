#!/bin/sh

# Initialize variables
requester_name=""
message_id=""
slice_id=""
output_folder=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
    key="$1"
    case $key in
        --requester_name|-r) # Set requester name
            requester_name="$2"
            shift # past argument
            shift # past value
            ;;
        -m|--message_id) # Set message ID
            message_id="$2"
            shift # past argument
            shift # past value
            ;;
        -s|--slice_id) # Set slice ID
            slice_id="$2"
            shift # past argument
            shift # past value
            ;;
        -o|--output_folder) # Set output folder
            output_folder="$2"
            shift # past argument
            shift # past value
            ;;
        *) # Handle unknown options
            echo "Unknown option $1"
            exit 1
    esac
done

# Check if requester_name is provided
if [ -z "$requester_name" ]; then
    echo "You need to specify --requester_name!"
    exit 1
fi

# Check if message_id is provided
if [ -z "$message_id" ]; then
    echo "You need to specify --message_id!"
    exit 1
fi

# Check if output_folder exists
if [ -z "$output_folder" ] || [ ! -d "$output_folder" ]; then
    echo "You need to specify a directory for the --output_folder option!"
    exit 1
fi

filename="../src/.env"
count=$(grep -c '^[^#]*''NAME="AUTH' "$filename")  # Count Authorities

# Run the Python script for each Authority
for i in $(seq 1 $count); do
    python3 ../src/client.py --handshake -a "$i" -r "$requester_name"
    python3 ../src/client.py --generate_key -a "$i" -r "$requester_name"
done

# Validate message_id format and find it if needed
if [ ${#message_id} -lt 18 ] || ! echo "$message_id" | grep -qE '^[0-9]+$'; then
    matching_lines=$(grep "$message_id" "../src/.cache")
    if [ $(echo "$matching_lines" | wc -l) -eq 1 ]; then
        message_id=$(echo "$matching_lines" | grep -oP '\b\d+\b')
    fi
fi

# Handle slice_id logic
if [ -z "$slice_id" ]; then
    python3 ../src/reader.py --message_id "$message_id" \
        --reader_name "$requester_name" --output_folder "$output_folder"
else
    if [ ${#slice_id} -lt 18 ] || ! echo "$slice_id" | grep -qE '^[0-9]+$'; then
        matching_lines=$(grep "$slice_id" "../src/.cache")
        if [ $(echo "$matching_lines" | wc -l) -eq 1 ]; then
            slice_id=$(echo "$matching_lines" | grep -oP '\b\d+\b')
        fi
    fi
    python3 ../src/reader.py --message_id "$message_id" --slice_id "$slice_id" \
        --reader_name "$requester_name" --output_folder "$output_folder"
fi

# Check if the last command was successful
if [ $? -ne 0 ]; then
    echo "Error: python3 command failed!"
else
    echo "✅ Data owner access done"
fi
