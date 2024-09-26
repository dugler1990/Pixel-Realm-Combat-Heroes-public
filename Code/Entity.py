from cmath import rect
import pygame
from math import sin
import os
import math
from hashRect import HashableRect
from Support import print_mask
# This is for file (images specifically) importing (This line changes the directory to where the project is saved)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
MAX_DISPLACEMENT = 5.5
class Entity(pygame.sprite.Sprite):
    # Class-level variable to keep track of IDs
    id_counter = 0
    def __init__(self, groups, layout_callback_update_quad_tree = None):
        super().__init__(groups)
        Entity.id_counter += 1
        self.id = Entity.id_counter
        self.frame_index = 0
        self.animation_speed = 0.25
        self.direction = pygame.math.Vector2()
        self.max_collision_distance_squared = 10000
        self.max_collision_distance = 10
        self.mask = None
        # Flag to track whether move method has been called before
        self.move_not_called_before = True
        if layout_callback_update_quad_tree :
            self.layout_callback_update_quad_tree = layout_callback_update_quad_tree
        else:
            def empty_func_is_not_nicey(*args, alive = True, remove_existing = True):pass
            self.layout_callback_update_quad_tree  =  empty_func_is_not_nicey
    #@profile
    def move(self, speed, QuadTree,entity_quad_tree, update_quad_tree = True):
        
        
        
        #print(f'speed as stated in move method: {speed}')
        #print(f"Quadtree in move method : {entity_quad_tree.manager.item_mapping}")
        #print( f"self.move_not_called_before : {self.move_not_called_before}" )
        remove_existing = not self.move_not_called_before
        #print(f"remove existing : {remove_existing}")
        if update_quad_tree:
            if hasattr(self, 'sprite_type'):
                sprite_type = self.sprite_type
            else:
                sprite_type = None
                
            if hasattr(self, 'mask'):
                mask = self.mask
            else:
                mask = None
        
        
        
            self.layout_callback_update_quad_tree(HashableRect(self.rect,
                                                               self.id,
                                                               self.direction,
                                                               sprite_type,
                                                               mask),
                                                  alive = True,
                                                  remove_existing = remove_existing)
            # Update flag after the first call
            self.move_not_called_before = False
        # if hasattr(self, "type" ): 
        #     if self.type == "player":
        #         print(f"hitbo pre : {self.hitbox}")
        #         print(f"self.animation spee : {self.animation_speed}")
     
        #print(f"attempting to move with speed : {speed}")
        #print(f"position before move : {self.pos}")
        #print(speed)
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
 
        #print("DIRECTION")
#        print(self.direction.x)
        
        
        #print(f"speed: {speed}")
#        print(self.animation_speed)
#        print(self.direction)
#        print(self.direction.magnitude())
        #print(f"rec center pre move  : {self.rect.center}")
        #print(f"hitbox pre move  : {self.hitbox.x}")
        #print(f"hitbox pre move  : {self.hitbox.y}")
        #print(f"direction : {self.direction}")
        #print(f"hitbo pre : {self.hitbox}")
        #print(f"direction x : {self.direction.x}")
        self.hitbox.x += self.direction.x * speed
        #print(f"hitbox post move  : {self.hitbox.x}")
        
        
        
        ### TODO :it seem like i am passing horizontal and vertical to collision wrongly, also, it only needs to be run once.
        
        
        #self.collision_old("Horizontal")
        #self.collision_old2("Horizontal")
        self.hitbox.y += self.direction.y * speed
        
        
        # if hasattr(self, "type" ): 
        #     if self.type == "player":
        #         print(f"hitbo pre : {self.hitbox}")
     
        
        #self.collision("Vertical",QuadTree=QuadTree)
        self.rect.center = self.hitbox.center
        #print(f"rec center post move  : {self.rect.center}")
        
        self.collision(  
                        QuadTree=QuadTree ,
                        entity_quad_tree = entity_quad_tree,
                        speed = speed
                        )
        


    #@profile
    def collision(self, QuadTree, entity_quad_tree, speed = 0):# Speed is just to adjust displacement when colliding with objects so you dont go through
                                                                  # Maybe i should do the same with entity collisions.
        
        """
        Issues with this function : i have a bunch of conditions and each one actually
        moved the player, as opposed to keeping track of a displacement, 
        this is because if there is a collision and then we notice a obstacle collision of the deflection of that 
        collision, we do not make the movement change in terms of displacement, we use the obstacle 
        boundry. We could surely fix this but this is just so that you dont get too lost.
        
        explanation of function 
        
        check collisions with any obstacles, if that happens, thats all that happens, 
        
        if there are no imediate obstacle collisions, check entity collisions, 
        
            if entity is stationary , consider the collision like into a wall
                 TODO, they should take some impact depending on size
                 
            if the entity is moving, we do some basic calcs about increasing rebound based on relative velocity
            but we just rebound on the normal of the collision , rbound is larger if the entity is bigger
            
            if rebounding from an entity would result in you colliding with an object, you appear at theb oundry of the object
            im still worrid you could get hit simultansouly by a bunch of entites and go through an obstacle
            lets see.
            
            seems to work ok , being in a corner ( secondary collision with vertical and horizontal wall can go wrong.)
            
            would be cool if there was some dampening some how, like, at the moment if you get stuck in a corner
            you bound around like crazy, would be nice if... you needed speed for that, i dno.
        
        
            """
            
            
        # Define displacement for collision resolution with obstacles
        displacement_obstacles = 1  
        MAX_DISPLACEMENT = speed
        
        total_displacement_x = 0
        total_displacement_y = 0
        max_penetration_depth = 0
        
        # Define base displacement for entity collisions
        base_displacement_entities = 1.1  # Adjust this value as needed
        exponent = 4 # Adjust this exponent for the desired relationship
        
        # Check for nearby obstacles using the QuadTree
        nearby_obstacles = QuadTree.hit(HashableRect(self.rect, self.id))
        nearby_entities = entity_quad_tree.hit(HashableRect(self.rect, self.id))
        
        
        # if hasattr(self,'type'):
        #     if self.type == "player" :
        #         print_mask(self.mask)
        
        
        # if hasattr(self, 'monster_name'):
        #     if self.monster_name == 'raccoon':
            
        #         print(self.monster_name)
                #print(f"nearby obstacles : {nearby_obstacles}")
                
                #print(f"nearby entities : {nearby_entities}")
        
        
        # Iterate over nearby obstacles (walls)
        for obstacle in nearby_obstacles:
            do_collision = True
            if self.mask and obstacle.mask:
                # Calculate the difference between the center positions of the two entities
                dx = obstacle.rect.x - self.rect.x
                dy = obstacle.rect.y - self.rect.y
    
                overlap = self.mask.overlap_area(obstacle.mask, (dx, dy))
                if overlap == 0:
                    do_collision = False
    
            if do_collision:
                # Calculate the angle of collision relative to the entity's movement direction
                collision_normal = math.atan2(obstacle.rect.centery - self.rect.centery, obstacle.rect.centerx - self.rect.centerx)
                rebound_angle = collision_normal + math.pi
    
                # Calculate the penetration depth
                penetration_x = max(0, self.rect.right - obstacle.rect.left, obstacle.rect.right - self.rect.left)
                penetration_y = max(0, self.rect.bottom - obstacle.rect.top, obstacle.rect.bottom - self.rect.top)
                penetration_depth = math.sqrt(penetration_x**2 + penetration_y**2)**1.5
    
                # Update total displacement vector
                total_displacement_x += math.cos(rebound_angle)
                total_displacement_y += math.sin(rebound_angle)
    
                # Update the maximum penetration depth
                max_penetration_depth = max(max_penetration_depth, penetration_depth)
    
        # Normalize the total displacement direction
        displacement_magnitude = math.sqrt(total_displacement_x**2 + total_displacement_y**2)
        if displacement_magnitude > 0:
            total_displacement_x /= displacement_magnitude
            total_displacement_y /= displacement_magnitude
    
        # Scale the displacement based on the maximum penetration depth
        
        # print(displacement_obstacles)
        # print(max_penetration_depth)
        # print(MAX_DISPLACEMENT)
        
        scaled_displacement = min(displacement_obstacles + max_penetration_depth, MAX_DISPLACEMENT)
        # print("scaled_displacement")
        # print(scaled_displacement)
        # Apply the displacement to the entity's position
        self.hitbox.left += scaled_displacement * total_displacement_x
        self.hitbox.top += scaled_displacement * total_displacement_y
        # if hasattr(self,'type'):
        #     if self.type == "player" :
                
                
        #         print(f"displacement x : {scaled_displacement * math.cos(total_displacement_x)}")
        #         print(f"displacement y : {scaled_displacement * math.sin(total_displacement_y)}")
                

        # #print(dir(entity))
        # if hasattr(self, 'monster_name'):
        #     print("hey")
        #     print(self.monster_name)
        #     if self.monster_name == 'raccoon':
        #         print(f"nearby_obstacles :{nearby_obstacles} ")
        
        # If not colliding with a wall, handle entity collisions
        if not nearby_obstacles:
            for entity in nearby_entities:
                # Check if the other entity is stationary
                
                
                # #print(dir(entity))
                # if hasattr(self, 'monster_name'):
                #     print("hey")
                #     print(self.monster_name)
                #     if self.monster_name == 'raccoon':
                #         print(f"entity  direction :{entity.direction} ")
                        
                #         print(f"entity direction :{entity.direction.magnitude()} ")
                        
                #         print("self:")
                #         print_mask(self.mask)
                #         print("entity")
                #         print_mask(entity.mask)
                
                """
                so here , if the entity doesnt have a mask , because its nerby we collide, if it doesnt have a 
                mask, we just collide it anyway
                
                at the moment all enemies have masks and player, no neutrals or objects.
                
                what it seems like to me though, is that the images with the alpha were already acting like masks
                
                regardless, it will be good to be able to play with how the mask collisions happen.
                
                """
                
                do_colision = True
                if  self.mask and entity.mask:
                    #print("self:")
                    #print_mask(self.mask)
                    #print("entity")
                    #print_mask(entity.mask)
                    # Calculate the difference between the center positions of the two entities
                    dx = entity.rect.x - self.rect.x
                    dy = entity.rect.y - self.rect.y

                    overlap = self.mask.overlap_area( entity.mask, (dx,dy) )
                    # print('overlap')
                    # print(overlap)
                    if overlap == 0 :
                        
                        #print("both masks exist")
                        #print(overlap)
                        do_colision = False
                    
                # if hasattr(entity, 'sprite_type'):
                #     if entity.sprite_type == 'magic':
                #         print(f"magic direction :{entity.direction} ") 
                
                
                # if hasattr(entity, 'sprite_type'):
                #     if entity.sprite_type == 'player':
                #         print(f"player direction :{entity.direction} ") 
                
                    
                if do_colision and entity.direction:
                    
                    
                    if entity.direction.magnitude() == 0  :
                        # second or is just because of an error, shouldnt exist, player can have None? particle maybe ?
                    
                        
                        angle_radians = math.atan2(self.direction.y, self.direction.x)
                        angle_degrees = math.degrees(angle_radians)
                        
                        
                   
                        
                        # Calculate the angle between the entity's direction and the collision normal
                        collision_normal = math.atan2(entity.rect.centery - self.rect.centery, entity.rect.centerx - self.rect.centerx)
                        
                        
                        # if hasattr(entity, 'sprite_type'):
                        #     if entity.sprite_type== 'Eskimo':
                        #         print(f"stationary eskimo collision normal :{collision_normal} ")
                        
                        # Calculate the rebound angle (opposite angle)
                        rebound_angle = collision_normal + math.pi 
                        
                        # Treat the stationary entity as an obstacle
                        displacement_x = displacement_obstacles * math.cos(rebound_angle)
                        displacement_y = displacement_obstacles * math.sin(rebound_angle)
                        self.hitbox.left += displacement_x  
                        self.hitbox.top += displacement_y
                    else:
                        # Calculate the size ratio of the colliding entities (for example, based on widths)
                        
                        
                        # TODO: am planning to make player size bigger, also make the collision 
                        #       size not just based on width.
                        
                        # It should also dobe the entity recieving the impact that gets this size adjustment
                        #  right now its like bigger objects are bouncy, it should be more like knowckback.
                        
                        size = (self.rect.width*self.rect.height) 
                        if hasattr(self,'type'):
                            if self.type == "player" :
                                size = (self.rect.width*self.rect.height) * 3.5
                        
                                
                        size_ratio = size / (entity.rect.width*entity.rect.height)
                        
                        
                        # Calculate the displacement based on the size ratio and apply it for entities
                        displacement_entities = base_displacement_entities + base_displacement_entities * (1 + math.exp(exponent * (1 - size_ratio)))
                        
                        # Calculate relative velocity (speed) between the entities
                        relative_velocity = self.direction.magnitude() - entity.direction.magnitude()
                        
                        # Calculate the direction vector from the other entity to self
                        direction_vector = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(entity.rect.center)
                        
                        # Calculate the angle between the direction vector and the collision normal
                        collision_normal = math.atan2(direction_vector.y, direction_vector.x)
                        
                        # Calculate the rebound angle based on the collision normal and relative velocity
                        rebound_angle = collision_normal 
                        #rebound_angle = collision_normal + math.pi
                        #rebound_angle = rebound_angle % (2 * math.pi)
                        
                        # Adjust the displacement based on the relative velocity
                        displacement_entities *= 1.5 if relative_velocity > 0 else 0.5 if relative_velocity < 0 else 1
                        
                        # Determine the direction of displacement based on the movement direction
                        displacement_x = displacement_entities * math.cos(rebound_angle)
                        displacement_y = displacement_entities * math.sin(rebound_angle)
                        
                        new_left = self.hitbox.left + displacement_x
                        new_top = self.hitbox.top + displacement_y
                        
                        #Check if the new position collides with any obstacles
                        obstacles_hit = QuadTree.hit(HashableRect(pygame.Rect(new_left, new_top, self.hitbox.width, self.hitbox.height), self.id))
                        #obstacles_hit=False
                        # if hasattr(self,'type'):
                        #     if self.type == "player" :
                        #         print(f"entity.direction: {entity.direction}")
                        #         print(f"self.direction: {self.direction}")
                        #         print(f"relative_velocity: {relative_velocity}")
                        #         print(f"self.direction.magnitude() : {self.direction.magnitude() }")
                        #         print(f"entity.direction.magnitude(): {entity.direction.magnitude()}")
                        #         print(f"direction_vector: {direction_vector}")
                        #         print(f"collision_normal: {collision_normal}")
                        #         print(f"displacement_y: {displacement_y}")
                        #         print(f"displacement_x: {displacement_x}")
                            
                        
                        # If there are obstacles in the path, adjust the position
                        if obstacles_hit:
                            obstacle = next(iter(obstacles_hit))  # Get the closest obstacle
                            if self.rect.left < obstacle.left:  # Intersection with left side
                                self.hitbox.right = obstacle.left
                                self.hitbox.top = new_top
                            elif self.rect.left > obstacle.right:  # Intersection with right side
                                self.hitbox.left = obstacle.right
                                self.hitbox.top = new_top
                            elif self.rect.top < obstacle.top:  # Intersection with top side
                                self.hitbox.bottom = obstacle.top
                                self.hitbox.left = new_left
                            else:  # Intersection with bottom side
                                self.hitbox.top = obstacle.bottom
                                self.hitbox.left = new_left
                        else:
                            #Move the entity to the calculated new position
                            self.hitbox.left += displacement_x
                            self.hitbox.top += displacement_y
                            
                            
                        
                    #     if hasattr(entity, 'sprite_type'):
                    #         if entity.sprite_type== 'PolarBear':
                    #             print(f"Polarbear size_ratio :{size_ratio} ")
                    #             print(f"Polarbear direction_vector :{direction_vector} ")
                    #             print(f"Polarbear collision_normal :{collision_normal} ")
                    #             print(f"Polarbear rebound_angle:{rebound_angle} ")
                    #             print(f"Polarbear relative_velocity :{relative_velocity} ")
                    #             print(f"Polarbear displace x :{displacement_x} ")
                    #             print(f"Polarbear displace y :{displacement_y} ")
                    # # Move the entity to the calculated new position



    #@profile
    def collision__(self, QuadTree, entity_quad_tree):
        # Define displacement for collision resolution with obstacles
        displacement_obstacles = 20  # Adjust this value as needed
        
        # Define base displacement for entity collisions
        base_displacement_entities = 10  # Adjust this value as needed
        exponent = 3 # Adjust this exponent for the desired relationship
        
        # Check for nearby obstacles using the QuadTree
        nearby_obstacles = QuadTree.hit(HashableRect(self.rect, self.id))
        nearby_entities = entity_quad_tree.hit(HashableRect(self.rect, self.id))
        
        # Iterate over nearby obstacles (walls)
        for obstacle in nearby_obstacles:
            # Calculate the angle of collision relative to the entity's movement direction
            angle_radians = math.atan2(self.direction.y, self.direction.x)
            angle_degrees = math.degrees(angle_radians)
            
            # Calculate the angle between the entity's direction and the collision normal
            collision_normal = math.atan2(obstacle.rect.centery - self.rect.centery, obstacle.rect.centerx - self.rect.centerx)
            
            # Calculate the rebound angle (opposite angle)
            rebound_angle = collision_normal + math.pi 
            
            # Adjust the position of the entity based on the rebound angle for obstacles
            self.hitbox.left += displacement_obstacles * math.cos(rebound_angle)
            self.hitbox.top += displacement_obstacles * math.sin(rebound_angle)
        
        # If not colliding with a wall, handle entity collisions
        if not nearby_obstacles:
            for entity in nearby_entities:
                # Calculate the size ratio of the colliding entities (for example, based on widths)
                
                #print(f"size ratio : {size_ratio}")
                # Calculate the displacement based on the size ratio and apply it for entities
                
                
                if hasattr(self,'type'):
                    if self.type == "player" :
                        self_size = self.rect.width*20
                        #print(self.rect.size)
                    else: self_size = self.rect.width
                        #print(f"entity.direction: {entity.direction}")
                size_ratio = self_size / entity.rect.width
                
                displacement_entities = base_displacement_entities + base_displacement_entities * (1 + math.exp(-exponent * (1 - size_ratio)))
                #print(displacement_entities)
                # Calculate relative velocity (speed) between the entities
                relative_velocity = self.direction.magnitude() - entity.direction.magnitude()
                # Calculate the direction vector from the other entity to self
                
                
                
                
                
                #### Here if the other entity is stationary, we just get the direction of self as with wall
                #     Regardless, this must be what is going wrong.
                
                direction_vector = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(entity.rect.center)
                
                # Calculate the angle between the direction vector and the collision normal
                collision_normal = math.atan2(direction_vector.y, direction_vector.x)
                
                # Calculate the rebound angle based on the collision normal and relative velocity
                rebound_angle = collision_normal + math.pi
               # # Adjust the displacement based on the relative velocity
                # if relative_velocity > 0:  # Entities are moving towards each other
                #     displacement_entities *= 1.5  # Increase displacement
                # elif relative_velocity < 0:  # Entities are moving away from each other
                #     displacement_entities *= 0.5  # Decrease displacement
                
                
                displacement_y = displacement_entities * math.sin(rebound_angle)
                displacement_x = displacement_entities * math.cos(rebound_angle)
                     
                    # if math.sin(rebound_angle) > 0:
                    #     displacement_y *= -1
                    
                    # # # Adjust displacement_x based on the sign of math.cos(rebound_angle)
                    # if math.cos(rebound_angle) > 0:
                    #     displacement_x *= -1
               
                    # #displacement_x *= abs(math.sin(collision_normal))
                    # #displacement_y *= abs(math.cos(collision_normal))
           
                # Determine which vertex to adjust based on the rebound angle
                #if rebound_angle < math.pi:  
                #new_left = self.rect.left + displacement_x
                #new_top = self.rect.top + displacement_y
                #else:  # Collision from the left or above
                #    new_left = self.rect.left - displacement_x
                #    new_top = self.rect.top - displacement_y            
               
                # new_left = self.rect.left + displacement_x
                # new_top = self.rect.top + displacement_y
                
                # Check if the new position collides with any obstacles
                # obstacles_hit = QuadTree.hit(HashableRect(pygame.Rect(new_left, new_top, self.hitbox.width, self.hitbox.height), self.id))
                # obstacles_hit=False
                # if hasattr(self,'type'):
                #     if self.type == "player" :
                #         print(f"entity.direction: {entity.direction}")
                #         print(f"self.direction: {self.direction}")
                #         print(f"relative_velocity: {relative_velocity}")
                #         print(f"self.direction.magnitude() : {self.direction.magnitude() }")
                #         print(f"entity.direction.magnitude(): {entity.direction.magnitude()}")
                #         print(f"direction_vector: {direction_vector}")
                #         print(f"collision_normal: {collision_normal}")
                #         print(f"displacement_y: {displacement_y}")
                #         print(f"displacement_x: {displacement_x}")
                    
                
                # # If there are obstacles in the path, adjust the position
                # if obstacles_hit:
                #     obstacle = next(iter(obstacles_hit))  # Get the closest obstacle
                #     if self.rect.left < obstacle.left:  # Intersection with left side
                #         self.hitbox.right = obstacle.left
                #         self.hitbox.top = new_top
                #     elif self.rect.left > obstacle.right:  # Intersection with right side
                #         self.hitbox.left = obstacle.right
                #         self.hitbox.top = new_top
                #     elif self.rect.top < obstacle.top:  # Intersection with top side
                #         self.hitbox.bottom = obstacle.top
                #         self.hitbox.left = new_left
                #     else:  # Intersection with bottom side
                #         self.hitbox.top = obstacle.bottom
                #         self.hitbox.left = new_left
                #else:
                    # Move the entity to the calculated new position
                self.hitbox.left += displacement_x
                self.hitbox.top += displacement_y
        
          
    def line_rect_intersection(start_point, end_point, rect):
        x1, y1 = start_point
        x2, y2 = end_point
    
        # Determine the side of the rectangle the line intersects with
        if x1 < rect.left:  # Intersection with left side
            x = rect.left
            y = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        elif x1 > rect.right:  # Intersection with right side
            x = rect.right
            y = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
        elif y1 < rect.top:  # Intersection with top side
            y = rect.top
            x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
        else:  # Intersection with bottom side
            y = rect.bottom
            x = x1 + (x2 - x1) * (y - y1) / (y2 - y1)
    
        return x, y
          
              
    ###@profile
    def collision_old3(self, direction):
        for sprite in self.obstacle_sprites:
            # Calculate the distance between the entity and the obstacle sprite
            #print(f"sprite.rect.center:{sprite.rect.center}, self.hitbox.center : {self.hitbox.center}")
            #distance = pygame.math.Vector2(sprite.rect.center) - pygame.math.Vector2(self.hitbox.center)
            # Check if the obstacle is within the maximum collision distance
            #if distance.length() <= self.max_collision_distance.length():
                         # Calculate the distance between the entity and the obstacle sprite
            dx = sprite.rect.centerx - self.hitbox.centerx
            dy = sprite.rect.centery - self.hitbox.centery
            if min(dx,dy) < 100:
            #print(dy)
            #print(dx)
            #distance_squared = dx ** 2 + dy ** 2
            #print(distance_squared)
            # Check if the obstacle is within the maximum collision distance
            #if distance_squared <= self.max_collision_distance_squared:
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == "Horizontal":
                        if self.direction.x > 0:  # Moving Right
                            self.hitbox.right = sprite.hitbox.left
                        elif self.direction.x < 0:  # Moving Left
                            self.hitbox.left = sprite.hitbox.right
                    
                    elif direction == "Vertical":
                        if self.direction.y > 0:  # Moving Down
                            self.hitbox.bottom = sprite.hitbox.top
                        elif self.direction.y < 0:  # Moving Up
                            self.hitbox.top = sprite.hitbox.bottom
                    return
                
    ###@profile
    def collision_old2(self, direction):
        if direction == "Horizontal":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # Moving Right
                        self.hitbox.right = sprite.hitbox.left
                    elif self.direction.x < 0: # Moving Left
                        self.hitbox.left = sprite.hitbox.right
                    return                  
        if direction == "Vertical":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # Moving Down
                        self.hitbox.bottom = sprite.hitbox.top
                    elif self.direction.y < 0: # Moving Up
                        self.hitbox.top = sprite.hitbox.bottom
                    return
    ###@profile
    def collision_old(self, direction):
        if direction == "Horizontal":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # Moving Right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # Moving Left
                        self.hitbox.left = sprite.hitbox.right
                        
        if direction == "Vertical":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # Moving Down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # Moving Up
                        self.hitbox.top = sprite.hitbox.bottom

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        else:
            return 0
