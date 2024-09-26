from PIL import Image

def crop_transparent_space(image_path, output_path):
    image = Image.open(image_path)
    image = image.convert("RGBA")

    # Find the bounding box of the non-transparent pixels
    bbox = image.getbbox()
    if bbox:
        # Crop the image to the bounding box
        cropped_image = image.crop(bbox)
        cropped_image.save(output_path)
    else:
        print("No non-transparent pixels found in image.")

# Example usage
crop_transparent_space("../Graphics/Level3Tiles/cabin_wall_inside_right.png", "../Graphics/Level3Tiles/cabin_wall_inside_right.png")
