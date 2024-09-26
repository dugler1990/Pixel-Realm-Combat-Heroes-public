import pygame

class AttackSlot:
    def __init__(self, rect, attack_type="general", angle=0, icon_path = None):
        self.rect = rect
        self.attack_type = attack_type
        self.angle = angle
        self.attack = None
        self.icon_path = icon_path
        self.attack_icon = pygame.image.load(self.icon_path).convert_alpha() if self.icon_path else None


    def draw(self, screen, selected = False, held_icon=None):



        # Handle slot rotation CHAT GPT DECIDED TO COMPLICATE STUFF WITH ROTATION HERE AND I DIDNT REALIZE, SICK
        if self.angle != 0:
            # Create a surface for the slot with transparency
            slot_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            # Determine the color based on the attack type
            color = (0, 255, 0) if self.attack_type == "magic" else (255, 255, 255)
            # Draw the rectangle on the slot surface with the determined color
            pygame.draw.rect(slot_surface, color, slot_surface.get_rect())
            # Rotate the slot surface according to the angle
            rotated_slot = pygame.transform.rotate(slot_surface, self.angle)
            # Blit the rotated slot surface to the screen at the slot's center
            screen.blit(rotated_slot, rotated_slot.get_rect(center=self.rect.center))
        else:
            # If the slot is not rotated, determine the color and draw the rectangle directly on the screen
            color = (0, 255, 0) if self.attack_type == "magic" else (255, 255, 255)
            pygame.draw.rect(screen, color, self.rect, 2)  # The thickness of 2 is arbitrary, adjust as needed

        # Draw attack icon if it exists
        if self.attack_icon:  # Use self.attack_icon directly
            # No need to reload the icon here, just use the one loaded in __init__
            attack_icon_scaled = pygame.transform.scale(self.attack_icon, (self.rect.width, self.rect.height))
            if self.angle != 0:
                # Rotate the scaled attack icon as well if there's an angle
                attack_icon_scaled = pygame.transform.rotate(attack_icon_scaled, self.angle)
                # Blit the rotated attack icon to the screen at the slot's center
                screen.blit(attack_icon_scaled, attack_icon_scaled.get_rect(center=self.rect.center))
            else:
                # Blit the scaled icon to the top left corner of the slot if no rotation
                screen.blit(attack_icon_scaled, self.rect.topleft)

        if selected:
            pygame.draw.rect(screen, (0, 0, 0), self.rect, 3)  # Draw a thicker black border for selected slot

                # Draw a smaller version of the held icon at the top right if this slot is selected
        if selected and held_icon:
            mini_icon = pygame.transform.scale(held_icon, (25, 25))  # Scale down the icon
            mini_icon_rect = mini_icon.get_rect(topright=self.rect.topright)
            screen.blit(mini_icon, mini_icon_rect)


class AttackSelection:

    def __init__(self, player, input_manager):
        self.visible = False
        self.slots = []
        self.input_manager = input_manager
        self.player = player
        self.held_icon = None 


        # Setup for magic attack slots on the left
        base_x, base_y = 50, 50
        max_magic_slots = 3  # Maximum of 3 magic attack slots

        self.selected_row = 0 
        self.selected_col = 0
        self.in_magic_slots = True
        self.grid_columns = 4  # 4x4 grid on the right
        self.grid_rows = 4
        self.magic_slots = 3  # 3 magic slots on the left

       
        # Create slots for the player's magic attacks or empty slots if less than 3
        for i in range(max_magic_slots):
            if i < len(player.magic_available):
                magic_key = list(player.magic_available.keys())[i]
                magic_info = player.magic_available[magic_key]
                icon_path = magic_info['graphic']
            else:
                icon_path = None  # Path to an empty slot image or None

            self.slots.append(AttackSlot(pygame.Rect(base_x + i * 110, base_y, 100, 100), "magic", 0, icon_path))

        # Setup for magic attack grid (4x4) or any other UI elements
        grid_x, grid_y = 320, 100
        for i in range(4):  # Rows
            for j in range(4):  # Columns
                x = grid_x + j * 110
                y = grid_y + i * 110
                self.slots.append(AttackSlot(pygame.Rect(x, y, 100, 100)))

    def toggle_visibility(self):
        self.visible = not self.visible

    def display(self, screen):
        if self.visible:
            # Draw background for attack selection area
            bg_rect = pygame.Rect(20, 20, 750, 500)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((128, 128, 128, 100))
            screen.blit(bg_surface, bg_rect.topleft)

            # Iterate through all slots to draw them
            for i, slot in enumerate(self.slots):
                selected = False
                if self.in_magic_slots and i < self.magic_slots:
                     # If we are in magic slots and it's one of the first three slots
                    selected = (i == self.selected_row)
                elif not self.in_magic_slots and i >= self.magic_slots:
                    # If we are in the grid, adjust the index for the grid starting point
                    grid_index = i - self.magic_slots
                    row = grid_index // self.grid_columns  # Determine the row in the grid
                    col = grid_index % self.grid_columns   # Determine the column in the grid
                    selected = (row == self.selected_row and col == self.selected_col)

                # Draw the slot with the selected state
                slot.draw(screen, selected=selected, held_icon=self.held_icon if selected else None)

            # Display title for magic selection
            font = pygame.font.Font(None, 36)
            title = font.render("Select Your Magic Attack", True, (255, 0, 0))
            screen.blit(title, (320, 50))

    def is_slot_selected(self, index):
        if self.in_magic_slots and index < self.magic_slots:
            return index == self.selected_row
        elif not self.in_magic_slots and index >= self.magic_slots:
            grid_index = index - self.magic_slots
            row = grid_index // self.grid_columns
            col = grid_index % self.grid_columns
            return row == self.selected_row and col == self.selected_col
        return False


    def get_current_slot_index(self):
        if self.in_magic_slots:
            return self.selected_row  # Magic slots index directly matches selected_row
        else:
            # Calculate index for the grid
            return self.magic_slots + self.selected_row * self.grid_columns + self.selected_col


    def input(self):

        if self.in_magic_slots:
            if self.input_manager.is_key_just_pressed(pygame.K_RIGHT) and self.selected_row < self.magic_slots - 1:
                # Navigate right within the magic slots
                self.selected_row += 1
            elif self.input_manager.is_key_just_pressed(pygame.K_LEFT) and self.selected_row > 0:
                # Navigate left within the magic slots
                self.selected_row -= 1
            elif self.input_manager.is_key_just_pressed(pygame.K_RIGHT) and self.selected_row == self.magic_slots - 1:
                # Move to the grid on the right, top-left corner
                self.in_magic_slots = False
                self.selected_row = 0
                self.selected_col = 0
        # Handle input within the grid
        else:
            if self.input_manager.is_key_just_pressed(pygame.K_DOWN):
                self.selected_row = min(self.selected_row + 1, self.grid_rows - 1)
            elif self.input_manager.is_key_just_pressed(pygame.K_UP):
                self.selected_row = max(0, self.selected_row - 1)
            elif self.input_manager.is_key_just_pressed(pygame.K_RIGHT):
                self.selected_col = min(self.selected_col + 1, self.grid_columns - 1)
            elif self.input_manager.is_key_just_pressed(pygame.K_LEFT):
                self.selected_col = max(0, self.selected_col - 1)
                if self.selected_col == 0 and self.input_manager.is_key_just_pressed(pygame.K_LEFT):
                    # Move back to the magic slots, right-most slot
                    self.in_magic_slots = True
                    self.selected_row = self.magic_slots - 1
        
        if self.input_manager.is_key_just_pressed(pygame.K_RETURN):
            index = self.get_current_slot_index()
            if self.held_icon is None and self.slots[index].attack_icon:
                # Pick up the icon
                self.held_icon = self.slots[index].attack_icon
                self.slots[index].attack_icon = None  # Empty the slot
            elif self.held_icon and not self.slots[index].attack_icon:
                # Drop the icon in the empty slot
                self.slots[index].attack_icon = self.held_icon
                self.held_icon = None  # No icon is held now
                
        
        # Exit with alt q or esc
        current_time = pygame.time.get_ticks()
        if self.input_manager.is_key_just_pressed(pygame.K_ESCAPE) or \
            (self.input_manager.is_key_pressed(pygame.K_LALT) or self.input_manager.is_key_pressed(pygame.K_RALT)) and \
            self.input_manager.is_key_just_pressed(pygame.K_q):
            if current_time - self.player.last_q_press_time > 500:
                self.player.level.toggle_attack_selection()
                self.player.last_q_press_time = current_time

