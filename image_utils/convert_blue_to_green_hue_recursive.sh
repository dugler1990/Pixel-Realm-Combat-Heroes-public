#!/bin/bash

# Check if a directory is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

INPUT_DIR="$1"

# Function to process images
process_image() {
    local INPUT_IMAGE="$1"
    local OUTPUT_IMAGE="$2"

    # Replace blue hues with green hues
    convert "$INPUT_IMAGE" \
        -modulate 100,100,50 \
        -fuzz 20% -fill "rgb(0,255,0)" -opaque "rgb(0,0,255)" \
        "$OUTPUT_IMAGE"
}

# Export the function to be used in find's exec
export -f process_image

# Find and process all image files recursively
find "$INPUT_DIR" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.bmp" \) -exec bash -c 'process_image "$0" "${0%.*}_converted.${0##*.}"' {} \;

echo "Conversion complete for all images in $INPUT_DIR"
