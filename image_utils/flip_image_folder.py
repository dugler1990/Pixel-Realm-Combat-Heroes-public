import cv2
import os
import sys

def flip_images_in_directory(directory_path):
    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return

    # Flip each image in the directory
    for filename in os.listdir(directory_path):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            file_path = os.path.join(directory_path, filename)
            # Load the image with alpha channel if it's a PNG, else normally
            image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED if filename.endswith(".png") else 1)

            if image is not None:
                # Flip the image horizontally
                flipped_image = cv2.flip(image, 1)
                # Save the flipped image, overwriting the original file
                cv2.imwrite(file_path, flipped_image)
                print(f"Flipped and saved {file_path}")
            else:
                print(f"Failed to load the image {file_path}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_directory>")
    else:
        directory_path = sys.argv[1]
        flip_images_in_directory(directory_path)
