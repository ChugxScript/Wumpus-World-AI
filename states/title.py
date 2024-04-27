import os
import pygame
import gif_pygame as gif
from states.select_game_mode import SelectGameMode

class Title():
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.FPS = 60
        self.clock = pygame.time.Clock()        

        self.select_game_mode_1 = SelectGameMode(self.display, self.gameStateManager)

    def run(self):
        self.load_assets()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.gameStateManager.set_state(self.select_game_mode_1)
                    self.gameStateManager.get_state().run()
            
            self.display.fill((255, 255, 255))
            self.gif_obj.render(self.display, (0, 0))
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def load_assets(self):
        self.assets_dir = os.path.join("assets")
        self.states_dir = os.path.join(self.assets_dir, "states")
        self.gif_obj = gif.load(os.path.join(self.states_dir, "title.gif"))