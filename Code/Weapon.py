import pygame
class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.sprite_type = "weapon"
        direction = player.status.split("_")[0]
        direction = direction.capitalize()
        # Graphics
        full_path = f"../Graphics/Weapons/{player.weapon.capitalize()}/{direction}.png"
        self.image = pygame.image.load(full_path).convert_alpha()

        # Print the direction for debugging
        #print(f"Weapon direction: {direction}")

        # Placement
        if direction == "Right":
            self.rect = self.image.get_rect(midleft=player.rect.midright + pygame.math.Vector2(0, 16))
            #print(f"Weapon position (Right): {self.rect.topleft}")
        elif direction == "Left":
            self.rect = self.image.get_rect(midright=player.rect.midleft + pygame.math.Vector2(0, 16))
            #print(f"Weapon position (Left): {self.rect.topright}")
        elif direction == "Down":
            self.rect = self.image.get_rect(midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
            #print(f"Weapon position (Down): {self.rect.midtop}")
        else:  # Assuming Up
            self.rect = self.image.get_rect(midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))
            #print(f"Weapon position (Up): {self.rect.midbottom}")
