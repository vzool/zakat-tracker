#!/bin/bash

# Check if a filename is provided
if [[ -z "$1" ]]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

filename="$1"

if [[ ! -e "$filename" ]]; then
    echo "Error: File '$filename' not exists"
    exit 1
fi

# Extract version using Python and toml
version=$(bash version.sh)

# Extract base filename and extension separately
base_filename="${filename%.*}"
extension="${filename##*.}"

# Construct new filename
new_filename="${base_filename}-${version}.${extension}"

# Check if the new filename already exists
if [[ -f "$new_filename" ]]; then
    echo "Error: File '$new_filename' already exists"
    exit 1
fi

# Perform the rename
mv "$filename" "$new_filename"

# Compress the renamed file using zip
zip -r "${new_filename}.zip" "$new_filename"

echo "Successfully renamed '$filename' to '$new_filename'"
