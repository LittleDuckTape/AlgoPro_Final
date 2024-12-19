import os, pygame
from os import walk

def import_folder(path):
    surface_list = []

    #checks if path exists
    if not os.path.exists(path):
        print(f"Directory does not exist: {path}")
        return surface_list

    for root, _, files in walk(path):
        for file in files:
            if file.lower().endswith('.png'):  #only add .png files
                full_path = os.path.join(root, file)
                try:
                    image_surf = pygame.image.load(full_path).convert_alpha()
                    surface_list.append(image_surf)
                except pygame.error:
                    print(f'Error loading image: {full_path}')

    return surface_list