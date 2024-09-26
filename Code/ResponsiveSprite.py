class EnvironmentResponsiveSprite(pygame.sprite.Sprite):
    def __init__(self, pos, groups, image, affected_by_wind=False):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.affected_by_wind = affected_by_wind

    def react_to_wind(self, wind):
        if self.affected_by_wind and wind:
            # Example reaction to wind
            if wind.intensity > 5:
                # Implement the sprite's reaction to strong wind
                pass
