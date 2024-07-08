#!/bin/sh

# Initialize variables
action=""
message_id=""
slice_id=""
requester_name=""
output_folder=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    -g|--generate)
      action="generate"
      shift # past argument
      ;;
    -a|--access)
      action="access"
      shift # past argument
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
    -sa|--requester_name)
      requester_name="$2"
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
      ;;
  esac
done

# Validate input folder existence
if [ "$action" = "access" ] && [ -n "$output_folder" ] && [ ! -d "$output_folder" ]; then
  echo "Output folder '$output_folder' does not exist"
  exit 1
fi

# Run the Python script with the provided arguments
if [ "$action" = "generate" ]; then
  python3 ../src/reader.py --generate
  echo "✅ Data owner generate done"
elif [ "$action" = "access" ]; then
  python3 ../src/reader.py --access --message_id "$message_id" --slice_id "$slice_id" \
    --requester_name "$requester_name" --output_folder "$output_folder"
  echo "✅ Data owner access done"
else
  echo "No action specified. Use -g to generate or -a to access."
  exit 1
fi
