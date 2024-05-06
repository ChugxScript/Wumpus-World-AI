import os
import pygame
import gif_pygame as gif
from states.controls import Controls

class SelectWorldSize():
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager
        
        self.FPS = 60
        self.clock = pygame.time.Clock()

        self.assets_dir = os.path.join("assets")
        self.states_dir = os.path.join(self.assets_dir, "states")
        self.world_size_array = [
            'select_world_size_1',
            'select_world_size_2',
            'select_world_size_3',
            'select_world_size_4',
        ]
        self.index = 0
        self.current_world_size = self.world_size_array[self.index]

        self.controls = Controls(self.display, self.gameStateManager)
        
    def run(self, current_player):
        self.current_player = current_player
        self.load_assets()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.toggle_state('w')
                    if event.key == pygame.K_s:
                        self.toggle_state('s')
                    if event.key == pygame.K_RETURN:
                        self.gameStateManager.set_state(self.controls)
                        self.gameStateManager.get_state().run(self.current_player, self.current_world_size)
            
            self.display.fill((255, 255, 255))
            self.gif_obj.render(self.display, (0, 0))
            pygame.display.flip()
            self.clock.tick(self.FPS)
    
    def toggle_state(self, key):
        if key == 'w':
            self.index = (self.index - 1) % len(self.world_size_array)
            self.current_world_size = self.world_size_array[self.index]    
        if key == 's':
            self.index = (self.index + 1) % len(self.world_size_array)
            self.current_world_size = self.world_size_array[self.index]  
        
        self.gif_obj = gif.load(os.path.join(self.states_dir, f"{self.current_world_size}.gif"))

    def load_assets(self):
        self.gif_obj = gif.load(os.path.join(self.states_dir, f"{self.current_world_size}.gif"))
