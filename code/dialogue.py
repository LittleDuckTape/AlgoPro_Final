import pygame
import os
from settings import *

class DialogueBox:
    def __init__(self, screen, font_path, font_size, box_image_path, text="Dialogue text"):
        # Setup display
        self.screen = screen
        self.screen_width, self.screen_height = screen.get_size()

        # Font
        font_path = os.path.join(os.path.dirname(__file__), "../graphics/fonts/PressStart2P-vaV7.ttf")
        self.font = self.load_font(font_path, font_size)

        # Load dialogue box background image
        self.box_image_path = os.path.join(os.path.dirname(__file__), box_image_path)
        self.box_image = self.load_image(self.box_image_path)

        if not self.box_image:
            print(f"Warning: Unable to load image at {self.box_image_path}. Using fallback rendering.")

        # Scale and position the dialogue box at the center bottom
        self.box_image = pygame.transform.scale(self.box_image, (850, 200)) if self.box_image else None
        self.box_rect = pygame.Rect(0, 0, 850, 200)
        self.box_rect.midbottom = (self.screen_width // 2, self.screen_height - 10)

        # Text setup
        self.text = text
        self.text_color = GREY
        self.text_padding = 30
        self.text_area_width = self.box_rect.width - (2 * self.text_padding)
        self.text_area_top = self.box_rect.top + self.text_padding

        self.active = False

    def load_font(self, path, size):
        try:
            return pygame.font.Font(path, size)
        except FileNotFoundError:
            print(f"Error: Font file not found at {path}. Using default font.")
            return pygame.font.SysFont("Arial", size)

    def load_image(self, path):
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error:
            print(f"Error: Failed to load image {path}.")
            return None

    def update(self):
        if self.active:
            self.handle_input()
            self.render()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.deactivate()

    def render(self):
        if not self.active:
            return

        # Render dialogue box background
        if self.box_image:
            self.screen.blit(self.box_image, self.box_rect)
        else:
            pygame.draw.rect(self.screen, (0, 0, 0), self.box_rect)  # Fallback background
            pygame.draw.rect(self.screen, (255, 255, 255), self.box_rect, 2)  # Border

        # Render wrapped dialogue text
        self.render_wrapped_text()

    def render_wrapped_text(self):
        words = self.text.split(" ")
        wrapped_lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_surface = self.font.render(test_line, True, self.text_color)
            if test_surface.get_width() <= self.text_area_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = word

        if current_line:
            wrapped_lines.append(current_line)

        y_offset = self.text_area_top
        for line in wrapped_lines:
            line_surface = self.font.render(line, True, self.text_color)
            self.screen.blit(line_surface, (self.box_rect.left + self.text_padding, y_offset))
            y_offset += line_surface.get_height() + 5

        # Render prompt text at the bottom
        prompt_text = "[Press Escape to Exit]"
        prompt_surface = self.font.render(prompt_text, True, self.text_color)
        prompt_position = (
            self.box_rect.left + self.text_padding,
            self.box_rect.bottom - self.text_padding - prompt_surface.get_height()
        )
        self.screen.blit(prompt_surface, prompt_position)

    def update_text(self, new_text):
        if new_text:
            self.text = new_text
            # print(f"Updated dialogue text to: {self.text}")
        else:
            print("Warning: Tried to update dialogue with empty text.")

    def activate(self, text=None):
        if text:
            self.update_text(text)
        # print("Dialogue box activated.")
        self.active = True

    def deactivate(self):
        # print("Dialogue box deactivated.")
        self.active = False
