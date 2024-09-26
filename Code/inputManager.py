import pygame

class InputManager:
    def __init__(self):
        self.current_key_states = {}
        self.previous_key_states = {}
        self.key_press_events = {}

    def update(self, events):
        self.previous_key_states = self.current_key_states.copy()
        self.key_press_events = {}

        for event in events:
            if event.type == pygame.KEYDOWN:
                self.current_key_states[event.key] = True
                if not self.previous_key_states.get(event.key, False):
                    self.key_press_events[event.key] = True
                # Debug print for key down events
                #print(f"Key Down: {pygame.key.name(event.key)} - State: {self.current_key_states[event.key]}")
                #print(f"key states {self.current_key_states}")
                #print(f"prev key states {self.previous_key_states}")
                #print(f"press events {self.key_press_events}")
            elif event.type == pygame.KEYUP:
                self.current_key_states[event.key] = False
                # Debug print for key up events
                #print(f"Key Up: {pygame.key.name(event.key)} - State: {self.current_key_states[event.key]}")

    def is_key_pressed(self, key):
        return self.current_key_states.get(key, False)

    def is_key_just_pressed(self, key):
        return self.key_press_events.get(key, False)

    def reset(self):
        # Debug print before resetting
        print("Resetting InputManager states.")
        self.current_key_states = {}
        self.previous_key_states = {}
        self.key_press_events = {}
        # Debug print after resetting
        print("InputManager states reset.")
