#!/bin/bash

# Prompt for the relative path of the folder containing the images
echo "Enter the relative path of the folder containing the images:"
read image_folder

# Save the current directory and navigate to the image folder
pushd "$image_folder"

# Display the size of PNG files before optimization
echo "Size of PNG files before optimization:"
ls -lh *.png

# Store the total size of PNG files before optimization
size_before=$(du -csh *.png | grep total | awk '{print $1}')

# Loop through all png images in the specified directory
for file in *.png; do
    echo "Optimizing $file..."
    # Resize the image to 64x64 pixels
    convert "$file" -resize 64x64\! "$file"
    # Optimize the PNG file
    pngquant --ext .png --force 256 "$file"
    optipng "$file"
done

# Display the size of PNG files after optimization
echo "Size of PNG files after optimization:"
ls -lh *.png

# Store the total size of PNG files after optimization
size_after=$(du -csh *.png | grep total | awk '{print $1}')

# Calculate and display the gains in terms of file size
echo "File size before optimization: $size_before"
echo "File size after optimization: $size_after"
echo "Gains in file size: $(echo "$size_before - $size_after" | bc)"

echo "Optimization complete."

# Return to the original directory
popd
