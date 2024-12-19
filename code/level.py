import os
import pygame
import random
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from sky import *
from map import Map
from dialogue import DialogueBox

class Level:
    def __init__(self, screen):
        # Get display surface
        self.display_surface = screen

        # Sprite groups
        self.all_sprites = None  # Set up later
        self.collision_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        # Package & doors
        self.doors_assigned = False

        self.setup()

        # Weather / sky
        self.rain = Rain(self.all_sprites)
        self.raining = random.randint(0, 10) > 5
        self.sky = Sky()

        # Transition
        self.transition = Transition(self.reset, self.sky)

        # Dialogue
        font_path = os.path.join(os.path.dirname(__file__), "../graphics/fonts/PressStart2P-vaV7.ttf")
        box_image_path = os.path.join(os.path.dirname(__file__), "../graphics/ui/box.png")
        self.dialogue_box = DialogueBox(screen, font_path, 20, box_image_path)
        self.dialogue_active = False

        # Map
        self.map = Map(self.player, self.toggle_map)
        self.map_active = False

    def setup(self):
        # Load map
        map_path = os.path.join(os.path.dirname(__file__), "../data/map.tmx")
        self.tmx_data = load_pygame(map_path)

        # Define level boundaries
        self.level_width = self.tmx_data.width * TILE_SIZE
        self.level_height = self.tmx_data.height * TILE_SIZE
        self.level_bounds = {
            'left': 0,
            'top': 0,
            'right': self.level_width,
            'bottom': self.level_height
        }

        self.all_sprites = CameraGroup(self.level_width, self.level_height)

        # Create map layers & background
        self.create_map_layers(self.tmx_data)
        self.create_background()

        # Player-related setup
        self.create_player(self.tmx_data)

        # Packages & doors
        self.assign_packages_to_doors(self.tmx_data)

    def create_map_layers(self, tmx_data):
        # Define layer handling
        layer_definitions = {
            'Fence': [self.all_sprites, self.collision_sprites],
            'HouseWall': [self.all_sprites],
            'HouseDoor': [self.all_sprites],
            'HouseRoof': [self.all_sprites],
            'Water': [self.all_sprites],
            'Collision': [self.collision_sprites],
            'Decoration': [self.all_sprites],
            'Trees': [self.all_sprites, self.collision_sprites]
        }

        # Iterate through map layers
        for layer_name, groups in layer_definitions.items():
            if layer_name in ['Fence', 'HouseWall', 'HouseDoor', 'HouseRoof', 'Collision']:
                for x, y, surf in tmx_data.get_layer_by_name(layer_name).tiles():
                    Generic((x * TILE_SIZE, y * TILE_SIZE), surf, groups)
            
            elif layer_name == 'Water':
                water_path = os.path.join(os.path.dirname(__file__), "../graphics/water")
                water_frames = import_folder(water_path)
                for x, y, surf in tmx_data.get_layer_by_name(layer_name).tiles():
                    Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, groups)
            
            elif layer_name in ['Decoration', 'Trees']:
                for obj in tmx_data.get_layer_by_name(layer_name):
                    if hasattr(obj, 'image'):
                        if layer_name == 'Decoration':
                            WildFlower((obj.x, obj.y), obj.image, groups)

                        else:
                            Trees((obj.x, obj.y), obj.image, groups, obj.name)

    def create_background(self):
        ground_path = os.path.join(os.path.dirname(__file__), "../graphics/world/ground.png")
        Generic(
            pos=(0, 0),
            surf=pygame.image.load(ground_path).convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground']
        )

    def create_player(self, tmx_data):
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x, obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    interaction=self.interaction_sprites,
                    screen=self.display_surface,
                    toggle_dialogue_box=self.toggle_dialogue_box,
                    toggle_map=self.toggle_map
                )
                self.player.level_bounds = self.level_bounds
                self.player.inventory = {'packages': random.randint(7, 12)}
            
            if obj.name.startswith('Door'):
                Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

    def assign_packages_to_doors(self, tmx_data):
        if self.doors_assigned:
            return  # If packages are already assigned, do not reassign

        # Get the layer containing door objects
        doors_layer = tmx_data.get_layer_by_name('Player')  # The layer with the doors is called 'Player'
        
        doors = []
        for obj in doors_layer:
            if obj.name.startswith("Door"):  # Filter for objects with names starting with 'Door'
                door_name = obj.name  # Use unique door names for reference
                doors.append((obj.x, obj.y, door_name, obj))  # Store the door's position and name

        total_doors = len(doors)
        player_packages = self.player.inventory['packages']

        # Ensure that the number of assigned packages doesn't exceed player's inventory or the total number of doors
        assigned_packages = min(player_packages, total_doors)
        assigned_indices = set(random.sample(range(total_doors), assigned_packages))

        self.door_states = {}

        # Assign states to doors
        for idx, (x, y, door_name, obj) in enumerate(doors):
            assigned = idx in assigned_indices  # Whether the package is assigned to this door

            # Store the state of each door in the dictionary using its unique door name
            self.door_states[door_name] = {
                'package_assigned': assigned,
                'delivered': False
            }

            # print(f"Door {door_name} at ({x}, {y}) - Package assigned: {assigned}, State: {self.door_states[door_name]}") #DEBUG

        self.doors_assigned = True  # Mark doors as assigned

    def display_inventory(self):
        font_path = os.path.join(os.path.dirname(__file__), "../graphics/fonts/PressStart2P-vaV7.ttf")
        font = pygame.font.Font(font_path, 18) if os.path.isfile(font_path) else pygame.font.SysFont("Arial", 18)

        box_path = os.path.join(os.path.dirname(__file__), "../graphics/ui/box.png")
        box_image = pygame.image.load(box_path).convert_alpha()
        box_resized = pygame.transform.scale(box_image, (250, 70))
        box_position = (20, 20)
        self.display_surface.blit(box_resized, box_position)

        package_text = f'Packages: {self.player.inventory["packages"]}'
        text_surf = font.render(package_text, True, GREY)
        text_rect = text_surf.get_rect(center=(box_position[0] + box_resized.get_width() // 2,
                                               box_position[1] + box_resized.get_height() // 2))
        self.display_surface.blit(text_surf, text_rect)

    def handle_interactions(self):
        keys = pygame.key.get_pressed()  # Get the current state of all keys
        for sprite in self.interaction_sprites:
            if self.player.rect.colliderect(sprite.hitbox):  # Check if player is within the door hitbox
                # Check door states (whether package is assigned or delivered)
                door_state = self.door_states.get(sprite.name)

                if keys[pygame.K_f] and not getattr(self, 'interaction_occurred', False):
                    # Only interact if the key is pressed and the interaction hasn't already occurred
                    if door_state is None:
                        print(f"Error: Door {sprite.name} not found in door_states!") 
                        continue  # Exit this interaction if door doesn't exist

                    # Check interaction with the door
                    if door_state['package_assigned']:
                        if not door_state['delivered']:  # If the package hasn't been delivered yet
                            # Decrease the package count before activating the dialogue
                            self.player.inventory["packages"] -= 1
                            
                            # Show "Package delivered!" message
                            self.dialogue_box.activate("Package delivered!")
                            self.dialogue_active = True  # Dialogue box is active
                            
                            # Mark the door to update after the dialogue box closes
                            self.door_state_to_update = sprite.name  # Set the flag for delayed update
                            
                            # Set the delivered flag for this interaction
                            self.package_delivered = True
                            self.interaction_occurred = True  # Mark the interaction as occurred
                        else:
                            self.dialogue_box.activate("Package already delivered!")
                            self.dialogue_active = True
                    else:
                        # No package assigned
                        self.dialogue_box.activate("Wrong house!")
                        self.dialogue_active = True

            # Once the dialogue box closes, update the door state and reset the interaction flag
            if not self.dialogue_active and hasattr(self, 'door_state_to_update'):
                door_name = self.door_state_to_update
                door_state = self.door_states.get(door_name)
                if door_state is not None:
                    door_state['delivered'] = True  # Mark as delivered after dialogue box closes
                    delattr(self, 'door_state_to_update')  # Reset the flag
                    delattr(self, 'package_delivered')  # Reset the package delivered flag
                    delattr(self, 'interaction_occurred')  # Reset the interaction flag

    def toggle_dialogue_box(self, text=""):
        self.dialogue_active = not self.dialogue_active
        if self.dialogue_active:
            self.dialogue_box.activate(text)
        else:
            self.dialogue_box.deactivate()

    def toggle_map(self):
        if not self.dialogue_box.active:
            self.map_active = not self.map_active

    def reset(self):
        # print("Level reset triggered!")  # DEBUG
        self.sky.reset()
        self.setup()
        self.player.inventory['packages'] = random.randint(7, 12)
        self.doors_assigned = False #allows new assignments
        self.assign_packages_to_doors(self.tmx_data)

    def run(self, dt):
        # Drawing logic
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)

        # Updates
        if self.map_active:
            self.map.update()
        elif self.dialogue_active:
            self.dialogue_box.update()
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.dialogue_box.deactivate()
                self.dialogue_active = False
        else:
            self.all_sprites.update(dt)

        # Interaction
        self.handle_interactions()

        # Rain
        if self.raining and not self.map_active and not self.dialogue_active:
            self.rain.update()

        # Daytime
        self.sky.display(dt)

        # Transition
        self.transition.play(dt)

        # Inventory
        self.display_inventory()

        # Dialogue
        if self.dialogue_active:
            self.dialogue_box.render()

class CameraGroup(pygame.sprite.Group):
    def __init__(self, level_width, level_height):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.level_width = level_width
        self.level_height = level_height

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        self.offset.x = max(0, min(self.offset.x, self.level_width - SCREEN_WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.level_height - SCREEN_HEIGHT))

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
