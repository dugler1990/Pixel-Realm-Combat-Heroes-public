import pygame

class AnimationSprite(pygame.sprite.Sprite):
    def __init__(self, frames, position, speed, groups):
        super().__init__(groups)
        self.frames = frames
        self.image = frames[0]
        self.rect = self.image.get_rect()
        # Calculate the center position to adjust for the new larger image size
        image_width, image_height = self.image.get_size()
        # Setting the center of the rectangle to be the same as the passed position
        self.pos = (position[0], position[1])
        self.rect.center = (position[0], position[1])
        self.frame_index = 0
        self.animation_speed = speed
        self.last_update = pygame.time.get_ticks()

    def update(self, dt = None):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()  # Remove sprite after animation
            else:
                self.image = self.frames[self.frame_index]
                # Update rect to keep the image centered as it changes
                self.rect = self.image.get_rect(center=self.rect.center)
                self.last_update = now
