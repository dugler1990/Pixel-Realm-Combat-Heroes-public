import pygame
from Entity import Entity
from Particles import AnimationPlayer, ParticleEffect
from ImageCache import ImageCache

class Trap(Entity):
    def __init__(self,
                 pos,
                 groups,
                 image_path,
                 animation_player,
                 effect_type,
                 death_animation,
                 add_exp,                 
                 target_type="all",
                 trigger="timer",
                 lifespan=5000,
                 radius=100,
                 health=100,
                 exp_value=50):
        
        super().__init__(groups)
        self.image = ImageCache.load_image(image_path)  # Load image from cache
        self.rect = self.image.get_rect(center=pos)
        self.animation_player = animation_player
        self.effect_type = effect_type
        self.death_animation = death_animation
        self.target_type = target_type
        self.trigger = trigger
        self.lifespan = lifespan
        self.radius = radius
        self.spawn_time = pygame.time.get_ticks()
        self.active = True if trigger != "timer" else False
        self.health = health
        self.exp_value = exp_value
        self.add_exp = add_exp
        self.groups = groups
        #self.animations = self.load_animations()

    # def load_animations(self):
    #     # Use ImageCache to load animation frames
    #     return {
    #         "activate": ImageCache.load_folder(f"../Graphics/Traps/{self.effect_type}/activate"),
    #         "destroy": ImageCache.load_folder(f"../Graphics/Traps/{self.effect_type}/destroy")
    #     }

    def update(self, QuadTree,entity_quad_tree,dt=None):
        current_time = pygame.time.get_ticks()
        if self.trigger == "timer" and current_time - self.spawn_time >= self.lifespan:
            self.activate()
            self.kill()
        elif self.trigger == "proximity":
            # TODO ADD if explosive on timout or not
            if current_time - self.spawn_time >= self.lifespan:
                self.activate()
                self.kill()
        elif self.trigger == "continuous":
            if self.active:
                self.activate()

    # def check_proximity(self):
    #     targets = pygame.sprite.spritecollide(self, self.groups[0], False)
    #     for target in targets:
    #         if pygame.math.Vector2(target.rect.center).distance_to(self.rect.center) <= self.radius:
    #             self.activate()
    #             self.kill()
    #             break

    def activate(self):
        self.animation_player.create_particles(self.effect_type, self.rect.center, self.groups)
        print(f"IN ACTIVATE, trigger : {self.trigger}")
        if self.trigger == 'proximity':
            print("IN PROXIMITY ABOUT TO KILL")
            self.trigger_death_particles()
            self.kill()

    def get_damage(self, damage, damage_type="physical"):
        self.health -= damage
        if self.health <= 0:
            self.trigger_death_particles()
            self.kill()

    def trigger_death_particles(self):
        self.animation_player.create_particles(self.death_animation, self.rect.center, self.groups)
        print("Trap destroyed")


# Usage example, assuming ImageCache is properly initialized and ready to use
#animation_player = AnimationPlayer()
#groups = []  # Define your sprite groups as needed
#trap = Trap((100, 100), groups, '../Graphics/Traps/explosion/trap_image.png', animation_player, "explosion", "enemies")
