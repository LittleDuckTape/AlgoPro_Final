import pygame, os
from settings import *

class Transition:
	def __init__(self, reset, sky):
		#setup
		self.display_surface = pygame.display.get_surface()
		self.reset = reset
		self.sky = sky

		#overlay image
		self.image = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
		self.color = 255
		self.speed = 100

		#transition states
		self.state = "idle"
		self.message_timer = 0
		
		font_path = os.path.join(os.path.dirname(__file__), "../graphics/fonts/PressStart2P-vaV7.ttf")
		font = pygame.font.Font(font_path, 20)
		self.font = font

	def play(self, dt):
		# print(f"Transition state: {self.state}, Color: {self.color}, Sky reached_end_color: {self.sky.reached_end_color}") #DEBUG
		if self.state == "idle" and self.sky.reached_end_color:
			self.state = "fade_in"

		if self.state == "fade_in":
			self.color -= self.speed * dt
			if self.color <= 0:
				self.color = 0
				self.state = "message"
				self.message_timer = pygame.time.get_ticks()
				self.reset()  #reset the sky and level

		elif self.state == "message":
			current_time = pygame.time.get_ticks()
			if current_time - self.message_timer > 2000: #display msg for 2 secs
				self.state = "fade_out"
		
		elif self.state == "fade_out":
			self.color += self.speed * dt
			if self.color >= 255:
				self.color = 255
				self.state = "idle"
		
		if self.state != "idle":
			self.draw_transition()
	
	def draw_transition(self):
		int_color = max(0, min(255, int(self.color)))
		self.image.fill((int_color, int_color, int_color))
		self.display_surface.blit(self.image, (0,0), special_flags = pygame.BLEND_RGBA_MULT)

		if self.state == "message":
			text_surface = self.font.render("The Next Day...", True, WHITE)
			text_rect = text_surface.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
			self.display_surface.blit(text_surface, text_rect)
	
	def reset(self):
		self.sky.reset()
