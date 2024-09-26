#!/bin/bash

# Loop through all png images in the current directory
for file in *.png; do
    echo "Resizing $file to 64x64 pixels..."
    convert "$file" -resize 64x64\! "$file"
done

echo "All images have been resized."
