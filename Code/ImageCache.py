import pygame
import os

class ImageCache:
    cache = {}

    @staticmethod
    def load_image(path):
        """Load an image from a path, using the cache to avoid reloading from disk."""
        if path not in ImageCache.cache:
            # Load the image and store it in the cache if it's not already there
            ImageCache.cache[path] = pygame.image.load(path).convert_alpha()
        return ImageCache.cache[path]

    @staticmethod
    def load_folder(folder):
        """Load all images in a folder, treating them as a sequence of frames."""
        images = []
        for filename in sorted(os.listdir(folder)):
            full_path = os.path.join(folder, filename)
            # Use the load_image method to ensure each image is cached individually
            images.append(ImageCache.load_image(full_path))
        return images
