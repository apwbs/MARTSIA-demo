#!/bin/sh

action2=""
message_id=""
slice_id=""
reader_name=""
output_folder=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
  key="$1"
  case $key in
    -a|--access)
      action2="access"
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
    -ra|--reader_name)
      reader_name="$2"
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

# Validate output folder existence
if [ "$action2" = "access" ] && [ -n "$output_folder" ] && [ ! -d "$output_folder" ]; then
  echo "Output folder '$output_folder' does not exist"
  exit 1
fi

# Run the Python script with the provided arguments
if [ "$action2" = "access" ]; then
  python3 ../src/reader.py --generate_parameters
  echo "✅ Data owner generate parameters done"
  python3 ../src/reader.py --access --message_id "$message_id" --slice_id "$slice_id" \
    --reader_name "$reader_name" --output_folder "$output_folder"
  echo "✅ Data owner access done"
else
  echo "No action specified. Use --access to access!"
  exit 1
fi
