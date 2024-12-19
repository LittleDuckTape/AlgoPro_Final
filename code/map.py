import pygame, os
from pytmx.util_pygame import load_pygame
from settings import *

class Map:
    def __init__(self, player, toggle_map):
        # General setup
        self.player = player
        self.toggle_map = toggle_map
        self.display_surface = pygame.display.get_surface()

        # Load map
        tmx_path = os.path.join(os.path.dirname(__file__), "../data/map.tmx")
        self.tmx_data = load_pygame(tmx_path)

        # Set up map box dimensions
        self.box_width = 750
        self.box_height = 600
        self.box_surface = pygame.Surface((self.box_width, self.box_height))
        self.box_rect = self.box_surface.get_rect(center=self.display_surface.get_rect().center)

    def draw_map_box(self):
        # Calculate scaling factor to fit the map
        map_width = self.tmx_data.width * TILE_SIZE
        map_height = self.tmx_data.height * TILE_SIZE

        scale_x = self.box_width / map_width
        scale_y = self.box_height / map_height
        scale_factor = min(scale_x, scale_y)

        # Draw tile layers
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):  # Tile layers
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        scaled_tile_size = int(TILE_SIZE * scale_factor)
                        tile_x = int(x * scaled_tile_size)
                        tile_y = int(y * scaled_tile_size)
                        scaled_tile = pygame.transform.scale(tile, (scaled_tile_size, scaled_tile_size))
                        self.box_surface.blit(scaled_tile, (tile_x, tile_y))

        # Draw object layers
        for obj in self.tmx_data.objects:
            # Scale object position
            scaled_x = int(obj.x * scale_factor)
            scaled_y = int(obj.y * scale_factor)
            scaled_width = int(obj.width * scale_factor)
            scaled_height = int(obj.height * scale_factor)

            # Draw actual graphic
            if obj.image:
                scaled_image = pygame.transform.scale(obj.image, (scaled_width, scaled_height))
                self.box_surface.blit(scaled_image, (scaled_x, scaled_y))
        
        # Draw a border around the map box
        border_thickness = 5
        border_color = WHITE
        pygame.draw.rect(self.box_surface, border_color, self.box_surface.get_rect(), border_thickness)

        # Blit the map box onto the display
        self.display_surface.blit(self.box_surface, self.box_rect.topleft)

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.toggle_map()

    def update(self):
        self.input()
        self.draw_map_box()
