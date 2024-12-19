import pygame, os
from settings import *
from support import import_folder
from sprites import Generic
from random import randint, choice

class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.start_color = list(WHITE)
        self.end_color = (38, 101, 189)
        self.speed = 1
        self.reached_end_color = False

    def display(self, dt):
        self.reached_end_color = True
        for index, value in enumerate(self.end_color):
            if self.start_color[index] > value:
                self.start_color[index] = max(self.start_color[index] - self.speed * dt, value)  # Prevent going past target
                self.reached_end_color = False
            elif self.start_color[index] < value:
                self.start_color[index] = min(self.start_color[index] + self.speed * dt, value)  # Prevent overshooting
                self.reached_end_color = False
            
        # print(f'Sky color: {self.start_color}') #DEBUG

        #fill screen with overlay / color
        self.full_surf.fill(self.start_color)
        self.display_surface.blit(self.full_surf, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
    
    def reset(self):
        self.start_color = list(WHITE)
        self.reached_end_color = False

class Drop(Generic):
    def __init__(self, pos, surf, moving, groups, z):
        #general setup
        super().__init__(pos, surf, groups, z)
        self.life_time = randint(400, 500)
        self.start_time = pygame.time.get_ticks()

        #moving parts
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, dt):
        #movement
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

        #timer
        if pygame.time.get_ticks() - self.start_time >= self.life_time:
            self.kill()

class Rain:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites

        #rain drops
        rain_drop_path = os.path.join(os.path.dirname(__file__), "../graphics/rain/drops/")
        self.rain_drops = import_folder(rain_drop_path)

        #rain puddle
        rain_floor_path = os.path.join(os.path.dirname(__file__), "../graphics/rain/floor/")
        self.rain_floor = import_folder(rain_floor_path)

        #floor level
        ground_path = os.path.join(os.path.dirname(__file__), "../graphics/world/ground.png")
        ground_surface = pygame.image.load(ground_path)
        self.floor_w, self.floor_h = ground_surface.get_size()

    def create_floor(self):
        Drop(
            pos = (randint(0, self.floor_w), randint(0, self.floor_h)), 
            surf = choice(self.rain_floor), 
            moving = False, 
            groups = self.all_sprites, 
            z = LAYERS['rain floor']
        )

    def create_drops(self):
        Drop(
            pos = (randint(0, self.floor_w), randint(0, self.floor_h)), 
            surf = choice(self.rain_drops), 
            moving = True, 
            groups = self.all_sprites, 
            z = LAYERS['rain drops']
        )
    
    def update(self):
        self.create_floor()
        self.create_drops()