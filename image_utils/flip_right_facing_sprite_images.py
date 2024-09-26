import cv2
import os
import sys

def flip_images_in_right_facing_directories(root_directory):
    # Check if the root directory exists
    if not os.path.exists(root_directory):
        print(f"The directory {root_directory} does not exist.")
        return

    # Iterate over all directories in the root directory
    for folder_name in os.listdir(root_directory):
        # Check if the folder name ends with "_right_facing"
        if folder_name.endswith("_right_facing"):
            folder_path = os.path.join(root_directory, folder_name)
            
            # Create a corresponding "_left_facing" directory
            left_facing_folder_name = folder_name.replace("_right_facing", "_left_facing")
            left_facing_folder_path = os.path.join(root_directory, left_facing_folder_name)
            if not os.path.exists(left_facing_folder_path):
                os.makedirs(left_facing_folder_path)

            # Flip each image in the "_right_facing" directory
            for filename in os.listdir(folder_path):
                if filename.endswith(".png"):
                    file_path = os.path.join(folder_path, filename)
                    # Load the image with alpha channel
                    image = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

                    if image is not None:
                        # Flip the image horizontally
                        flipped_image = cv2.flip(image, 1)
                        flipped_file_name = os.path.splitext(filename)[0] + "_flipped.png"
                        flipped_file_path = os.path.join(left_facing_folder_path, flipped_file_name)
                        # Save the flipped image with alpha channel
                        cv2.imwrite(flipped_file_path, flipped_image)
                        print(f"Flipped and saved {flipped_file_path}")
                    else:
                        print(f"Failed to load the image {file_path}.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_directory>")
    else:
        directory_path = sys.argv[1]
        flip_images_in_right_facing_directories(directory_path)

