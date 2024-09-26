#!/bin/bash

# Prompt for the directory
read -p "Enter the directory path: " directory

# Check if the directory exists
if [ ! -d "$directory" ]; then
    echo "Error: Directory '$directory' not found."
    exit 1
fi

# Prompt for scaling percentage
read -p "Enter the scaling percentage (e.g., 200 for 200%): " scaling

# Function to resize images
resize_image() {
    local file="$1"
    echo "Resizing $file to ${scaling}%..."
    convert "$file" -resize ${scaling}% "$file"
}

# Export the function to be used in find's exec
export -f resize_image
export scaling

# Find and process all png files recursively
find "$directory" -type f -iname "*.png" -exec bash -c 'resize_image "$0"' {} \;

echo "All images in '$directory' and its subdirectories have been resized to ${scaling}%."

