import pygame, sys, os
from settings import *
from level import Level

# Automate deletion of tempCodeRunnerFile.py
temp_file = "tempCodeRunnerFile.py"
if os.path.exists(temp_file):
    os.remove(temp_file)
    # print(f"Removed {temp_file}")

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pygame.display.set_caption("Angel's Message")
		self.clock = pygame.time.Clock()
		self.level = Level(self.screen)

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.display.quit()
					pygame.quit()
					sys.exit()

			dt = self.clock.tick(FPS) / 1000
			self.level.run(dt)
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()