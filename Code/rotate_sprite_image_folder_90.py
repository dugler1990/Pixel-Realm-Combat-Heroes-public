from PIL import Image
import os
import sys

def rotate_images(folder_path, output_folder=None, degrees=90):
    if output_folder is None:
        output_folder = folder_path

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over all the files in the directory
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(folder_path, filename)
            img = Image.open(file_path)
            # Rotate the image
            img_rotated = img.rotate(-degrees, expand=True)
            # Save the rotated image to the output folder
            output_path = os.path.join(output_folder, filename)
            img_rotated.save(output_path)
            print(f"Rotated {filename} and saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_directory> [<output_directory>]")
        sys.exit(1)

    folder_path = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else None

    rotate_images(folder_path, output_folder)

