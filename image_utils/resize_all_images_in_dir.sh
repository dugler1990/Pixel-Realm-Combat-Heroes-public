#!/bin/bash

# Prompt for the relative path of the folder containing the images
echo "Enter the relative path of the folder containing the images:"
read image_folder

# Save the current directory and navigate to the image folder
pushd "$image_folder"

# Loop through all image files in the specified directory
for file in *.png; do
    echo "Resizing $file by increasing 50%..."
    # Resize the image by increasing its dimensions by 50%
    convert "$file" -resize 150% "$file"
done

echo "Image resizing complete."

# Return to the original directory
popd

