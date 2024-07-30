#!/bin/bash

# Check if a filename is provided
if [[ -z "$1" ]]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

filename="$1"

pip install toml --upgrade
pip install --upgrade pip

# Extract version using Python and toml
version=$(python3 -c '
import toml
with open("pyproject.toml", "r") as f:
    config = toml.load(f)
version = config["tool"]["briefcase"]["version"]
print(version)
')

# Check if version extraction was successful
if [[ -z "$version" ]]; then
    echo "Error: Could not extract version from pyproject.toml"
    exit 1
fi

# Get Git commit count
commit_count=$(git rev-list --count HEAD)

# Get Git commit hash (shortened to 7 characters)
commit=$(git rev-parse --short HEAD)

# Extract base filename and extension separately
base_filename="${filename%.*}"
extension="${filename##*.}"

# Construct new filename
new_filename="${base_filename}-v${version}-${commit}-${commit_count}.${extension}"

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
