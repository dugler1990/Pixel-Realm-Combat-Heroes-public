#!/bin/bash

# Prompt for directory path
read -p "Enter the directory path: " directory

# Check if the directory exists
if [ ! -d "$directory" ]; then
    echo "Error: Directory '$directory' not found."
    exit 1
fi

# Prompt for scaling percentage
read -p "Enter the scaling percentage to reduce width (e.g., 50 for 50% reduction): " scaling_percentage

# Loop through all png images in the specified directory
for file in "$directory"/*.png; do
    # Check if file exists
    if [ -f "$file" ]; then
        echo "Resizing $file to reduce width by ${scaling_percentage}%..."
        convert "$file" -resize ${scaling_percentage}%x100% "$file"
    fi
done

echo "All images in '$directory' have been resized to reduce width by ${scaling_percentage}%."
