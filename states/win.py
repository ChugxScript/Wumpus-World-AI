import os
import pygame
import gif_pygame as gif
# from title import Title

class Win():
    def __init__(self, display, gameStateManager):
        pygame.init()
        self.display = display
        self.gameStateManager = gameStateManager
        self.FPS = 60
        self.clock = pygame.time.Clock()      
        self.GREEN = (0, 255, 0)  

        # self.title = Title(self.display, self.gameStateManager)

    def run(self, player_score):
        self.load_assets()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            
            self.display.fill((255, 255, 255))
            self.gif_obj.render(self.display, (0, 0))
            self.player_score_text = self.font.render(f'{player_score}', True, self.GREEN)
            self.display.blit(self.player_score_text, (500, 435))
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def load_assets(self):
        self.assets_dir = os.path.join("assets")
        self.states_dir = os.path.join(self.assets_dir, "states")
        self.font_dir = os.path.join(self.assets_dir, "font")
        self.font = pygame.font.Font(os.path.join(self.font_dir, "PressStart2P-Regular.ttf"), 20)
        # self.gif_obj = gif.load(os.path.join(self.states_dir, "win.gif")) # without secret
        self.gif_obj = gif.load(os.path.join(self.states_dir, "win_1.gif"))