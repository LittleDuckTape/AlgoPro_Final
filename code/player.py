import pygame
from settings import *
from support import *
from random import randint

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, interaction, screen, toggle_map, toggle_dialogue_box):
        super().__init__(group)

        self.import_assets()
        self.status = 'down_idle'
        self.frame_index = 0

        #general setup
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.z = LAYERS['main']

        #movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200

        #collision
        self.hitbox = self.rect.copy().inflate((-126, -70))
        self.collision_sprites = collision_sprites

        #inventory
        self.inventory = {
            'packages': randint(7, 12)
        }

        #interaction
        self.interaction = interaction
        self.can_interact = True #flag to manage interaction cooldown
        self.toggle_dialogue_box = toggle_dialogue_box
        self.toggle_map = toggle_map

        #level boundaries
        self.level_bounds = LEVEL_BOUNDS

    def import_assets(self):
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
        }

        base_path = os.path.dirname(os.path.dirname(__file__))  #get parent directory of 'code'
        for animation in self.animations.keys():
            full_path = os.path.join(base_path, 'graphics', 'character', animation)
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += 4 * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def input(self):
        keys = pygame.key.get_pressed()

        #WASD controls
        if keys[pygame.K_w]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pygame.K_s]:
            self.direction.y = 1
            self.status = 'down'
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
            self.status = 'right'
        elif keys[pygame.K_a]:
            self.direction.x = -1
            self.status = 'left'
        else:
            self.direction.x = 0

        #door interaction
        if keys[pygame.K_f] and self.can_interact:
            self.can_interact = False #prevent repeated interaction
            collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, False)
            if collided_interaction_sprite:
                door = collided_interaction_sprite[0]
                # print(f"Interacting with {door.name}")  #DEBUG
                result = self.deliver_package(door)
                # print(result) #DEBUG
                self.toggle_dialogue_box()
        
        if not keys[pygame.K_f]:
            self.can_interact = True
        
        #open map
        if keys[pygame.K_m]:
            self.toggle_map()

    def get_status(self):
        #checks if player is not moving
        if self.direction.magnitude() == 0:
            #adds _idle to status
            self.status = self.status.split('_')[0] + '_idle'

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0: # moving right
                            self.hitbox.right = sprite.hitbox.left
                        elif self.direction.x < 0: # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                        
                    elif direction == 'vertical':
                        if self.direction.y > 0: # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        elif self.direction.y < 0: # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def move(self, dt):
        #normalize the direction vector (ensures consistent speed, even when moving diagonally)
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        #move player based on normalized direction and speed
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

        #ensure the player stays within level bounds
        if self.rect.left < self.level_bounds['left']:
            self.rect.left = self.level_bounds['left']
            self.pos.x = self.rect.centerx

        if self.rect.right > self.level_bounds['right']:
            self.rect.right = self.level_bounds['right']
            self.pos.x = self.rect.centerx

        if self.rect.top < self.level_bounds['top']:
            self.rect.top = self.level_bounds['top']
            self.pos.y = self.rect.centery

        if self.rect.bottom > self.level_bounds['bottom']:
            self.rect.bottom = self.level_bounds['bottom']
            self.pos.y = self.rect.centery

    def deliver_package(self, door):
        # print(f"Checking door: {door.name}, Package Assigned: {door.package_assigned}, Delivered: {door.delivered}")  # DEBUG
        # Check for package delivery to the door
        if door.package_assigned and not door.delivered:
            door.delivered = True
            door.package_assigned = False  # Mark as delivered
            # print(f"Package delivered to {door.name}!")  # DEBUG
            return "Package delivered!"
        elif door.delivered:
            return "Package delivered!"
        else:
            return "Wrong house!"

    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)