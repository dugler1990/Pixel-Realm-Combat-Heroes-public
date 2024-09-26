
from Settings import TILESIZE
class Item:
    def __init__(self,
                 image_path,
                  pos,
                  item_type,
                  item_id,
                  effect=None,
                  effect_type = '',
                  float_offset = 0,
                  float_speed = 0.3,
                  float_direction = 1,
                  float_amplitude = 5):

        #print(pos)
        self.pos = pos  # Position where the item should appear
        self.item_type = item_type  # Type of item (could dictate the effect or usage)
        self.effect = effect  # Optional effect or function that gets executed when used or picked up
        self.effect_type = effect_type
        self.item_id = item_id
        self.image_path = image_path
        self.float_offset = float_offset
        self.float_direction = float_direction
        self.float_speed = float_speed
        self.float_amplitude = float_amplitude
    def use(self, player):
        # This method defines what happens when the item is used or picked up.
        # It could directly apply an effect to the player, or add the item to the player's inventory for later use.
        if self.effect:
            self.effect(player)  # Apply the item's effect to the player, if any.

        # Additional logic for what happens when the item is used/picked up can be added here.
        # For example, you might want to remove the item from the game world, or trigger an animation.

    # You can add more methods here related to the item's logic, such as combining items, upgrading, etc.
