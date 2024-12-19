import pygame

#screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64
FPS = 60

LAYERS = {
    'water': 0,
    'ground': 1,
    'rain floor': 2,
    'house bottom': 3,
    'main': 4,
    'house top': 5,
    'rain drops': 6
}

LEVEL_BOUNDS = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

#colors
GREY = (70, 70, 70)
WHITE = [255, 255, 255]