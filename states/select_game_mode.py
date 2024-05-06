import os
import pygame
import gif_pygame as gif
from states.select_world_size import SelectWorldSize

class SelectGameMode():
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        self.FPS = 60
        self.clock = pygame.time.Clock()

        self.assets_dir = os.path.join("assets")
        self.states_dir = os.path.join(self.assets_dir, "states")
        self.current_player = 'select_game_mode_1'
        self.gif_obj = gif.load(os.path.join(self.states_dir, f"{self.current_player}.gif"))

        self.select_world_size = SelectWorldSize(self.display, self.gameStateManager)
        
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a or event.key == pygame.K_d:
                        self.toggle_state()
                    if event.key == pygame.K_RETURN:
                        self.gameStateManager.set_state(self.select_world_size)
                        self.gameStateManager.get_state().run(self.current_player)
            
            self.display.fill((255, 255, 255))
            self.gif_obj.render(self.display, (0, 0))
            pygame.display.flip()
            self.clock.tick(self.FPS)
    
    def toggle_state(self):
        if self.current_player == 'select_game_mode_1':
            self.current_player = 'select_game_mode_2'
        else:
            self.current_player = 'select_game_mode_1'
        
        self.gif_obj = gif.load(os.path.join(self.states_dir, f"{self.current_player}.gif"))
