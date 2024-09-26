import os
import argparse
import numpy as np
import cv2

def create_blank_image(width, height):
    # Create a blank transparent image
    return np.zeros((height, width, 4), dtype=np.uint8)

def scale_droplets_in_image(image_path, scaling_factor):
    # Load the image with an alpha channel
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Extract the alpha channel
    alpha_channel = image[:, :, 3]
    # Threshold the alpha channel to identify non-transparent regions
    _, binary_alpha = cv2.threshold(alpha_channel, 0, 255, cv2.THRESH_BINARY)

    # Find contours of droplets based on the binary alpha channel
    contours, _ = cv2.findContours(binary_alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a blank transparent image of the same size as the original image
    modified_image = create_blank_image(image.shape[1], image.shape[0])

    # Iterate over each droplet
    for index, contour in enumerate(contours):
        # Filter out small contours as noise
        if cv2.contourArea(contour) < 3:  # Adjust this threshold as needed
            continue
        # Get bounding box coordinates
        x, y, w, h = cv2.boundingRect(contour)
        # Draw a black outline around the contour
        cv2.drawContours(image, [contour], 0, (0, 0, 0, 255), thickness=1)

        # Scale the droplet
        new_width = int(w * scaling_factor)
        new_height = int(h * scaling_factor)

        # Extract the droplet from the original image and resize it
        droplet = image[y:y+h, x:x+w]
        scaled_droplet = cv2.resize(droplet, (new_width, new_height))
        # Add a single-pixel black outline around the scaled droplet
        #scaled_droplet = cv2.copyMakeBorder(scaled_droplet, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=(0, 0, 0, 255))

        # Calculate the center of the original droplet
        center_x = x + w // 2
        center_y = y + h // 2

        # Calculate the new bounding box coordinates after scaling
        new_x = int(center_x - new_width // 2)
        new_y = int(center_y - new_height // 2)

        # Place the scaled droplet onto the modified image at the new position
        modified_image[new_y:new_y+new_height, new_x:new_x+new_width] = scaled_droplet

    # Save the modified image with scaled droplets and transparency
    filename, ext = os.path.splitext(os.path.basename(image_path))
    modified_image_path = os.path.join(os.path.dirname(image_path), f"{filename}_modified{ext}")
    cv2.imwrite(modified_image_path, modified_image)

def scale_droplets_in_folder(folder_path, scaling_factor):
    # Get a list of all image files in the folder
    image_files = [file for file in os.listdir(folder_path) if file.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

    # Iterate over each image file
    for image_file in image_files:
        # Construct the full path to the image
        image_path = os.path.join(folder_path, image_file)

        # Call the function to scale droplets in the image
        scale_droplets_in_image(image_path, scaling_factor)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Scale droplets in images in a folder.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing images.")
    parser.add_argument("--scaling_factor", type=float, default=0.5, help="Scaling factor for droplets.")
    args = parser.parse_args()

    # Call the function to scale droplets in images in the folder
    scale_droplets_in_folder(args.folder_path, args.scaling_factor)
