#!/bin/bash

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

# Construct new filename
full_version="${version}-${commit}-${commit_count}"

echo "$full_version"
