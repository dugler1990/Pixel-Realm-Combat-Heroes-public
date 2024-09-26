import pygame
import math

class InventorySlot:
    def __init__(self, rect, slot_type="general", angle=0):
        self.rect = rect
        self.slot_type = slot_type
        self.angle = angle
        self.item = None

    def draw(self, screen):
        if self.angle != 0:
            # Create a new surface for the rotated slot
            slot_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            color = (255, 255, 255) if self.slot_type == "general" else (0, 255, 0)
            pygame.draw.rect(slot_surface, color, (0, 0, self.rect.width, self.rect.height))

            # Rotate the slot surface
            rotated_image = pygame.transform.rotate(slot_surface, self.angle)
            screen.blit(rotated_image, rotated_image.get_rect(center=self.rect.center))
        else:
            color = (255, 255, 255) if self.slot_type == "general" else (0, 255, 0)
            pygame.draw.rect(screen, color, self.rect, 2)


                    # If there's an item in the slot, draw it
        if self.item is not None:
            item_image = pygame.image.load(self.item.image_path).convert_alpha()  # Load the item image
            item_image = pygame.transform.scale(item_image, (self.rect.width, self.rect.height))  # Scale to fit the slot
            
            # If the slot is rotated, apply rotation
            if self.angle != 0:
                item_image = pygame.transform.rotate(item_image, self.angle)
            
            # Adjust image positioning based on rotation
            if self.angle != 0:
                screen.blit(item_image, item_image.get_rect(center=self.rect.center))
            else:
                screen.blit(item_image, self.rect.topleft)


class Inventory:
    def __init__(self, player, input_manager):
        self.visible = False
        self.slots = []
        self.input_manager = input_manager
        self.player = player

        # Base dimensions and position
        base_x, base_y = 50, 50
        slot_width, slot_height = 60, 60

        # Equipment slots
        # Helmet
        self.slots.append(InventorySlot(pygame.Rect(base_x + 70, base_y, 50, 50), "helmet"))
        # Armor
        self.slots.append(InventorySlot(pygame.Rect(base_x, base_y + 60, 180, 120), "armor"))

        # Arms (angled and positioned to the sides)
        arm_width, arm_height = 20, 140
        self.slots.append(InventorySlot(pygame.Rect(base_x - 25, base_y + 100, arm_width, arm_height), "arm", angle=30))
        self.slots.append(InventorySlot(pygame.Rect(base_x + 185, base_y + 100, arm_width, arm_height), "arm", angle=-30))

        # Weapons
        self.slots.append(InventorySlot(pygame.Rect(base_x - 10, base_y + 210, 45, 135), "weapon"))
        self.slots.append(InventorySlot(pygame.Rect(base_x + 145, base_y + 210, 45, 135), "weapon"))

        # Boots
        self.slots.append(InventorySlot(pygame.Rect(base_x - 20, base_y + 355, 80, 40), "boots"))
        self.slots.append(InventorySlot(pygame.Rect(base_x + 120, base_y + 355, 80, 40), "boots"))

        # Backpack grid 4x3
        backpack_x, backpack_y = 320, 100
        for i in range(4):  # Rows
            for j in range(3):  # Columns
                x = backpack_x + j * (slot_width + 10)
                y = backpack_y + i * (slot_height + 10)
                self.slots.append(InventorySlot(pygame.Rect(x, y, slot_width, slot_height)))

    def toggle_visibility(self):
        self.visible = not self.visible

    def display(self, screen):
        if self.visible:
            # Draw slightly transparent grey box around the inventory
            inventory_area = pygame.Rect(20, 20, 550, 500)
            transparent_surface = pygame.Surface((inventory_area.width, inventory_area.height), pygame.SRCALPHA)
            transparent_surface.fill((128, 128, 128, 100))  # RGBA: semi-transparent grey
            screen.blit(transparent_surface, inventory_area.topleft)

            for slot in self.slots:
                slot.draw(screen)

    def input(self):
        current_time = pygame.time.get_ticks()
        if self.input_manager.is_key_just_pressed(pygame.K_i):
            if current_time - self.player.last_i_press_time > 500:
                self.player.level.toggle_inventory()
                self.player.last_i_press_time = current_time


    def add_item(self, item):
        # Calculate the starting index for backpack slots
        # Assuming backpack grid is 4x3, there are 12 slots for the backpack
        backpack_start_index = len(self.slots) - 4 * 3  # Adjust this based on your actual number of backpack slots

        # Iterate over only the backpack slots to find an empty one
        for slot in self.slots[backpack_start_index:]:
            if slot.item is None:  # Slot is empty
                slot.item = item  # Assign the item to this slot
                print(f"item assigned:{item}")
                return True  # Item was successfully added to the backpack

        # If no empty slot was found
        print("Inventory is full.")  # Optional: Notify the player that the inventory is full
        return False  # Item could not be added

