import os
import pygame
import gif_pygame as gif

class Win():
    def __init__(self, display, gameStateManager):
        pygame.init()
        self.display = display
        self.gameStateManager = gameStateManager
        self.FPS = 60
        self.clock = pygame.time.Clock()      
        self.GREEN = (0, 255, 0)  

    def run(self, player_score):
        from states.title import Title
        self.load_assets()
        self.draw_rectangles()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for rect in self.rectangles:
                        if rect["rect"].collidepoint(mouse_x, mouse_y):
                            print("Rectangle clicked:", rect["id"])
                            if rect["id"] == 1:
                                pygame.quit()
                                quit()
                            if rect["id"] == 2:
                                self.gameStateManager.set_state(Title(self.display, self.gameStateManager))
                                self.gameStateManager.get_state().run()
            
            self.display.fill((255, 255, 255))
            self.gif_obj.render(self.display, (0, 0))
            self.player_score_text = self.font.render(f'{player_score}', True, self.GREEN)
            self.display.blit(self.player_score_text, (500, 435))
            self.draw_rectangles()
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def draw_rectangles(self):
        WHITE = (255,255 , 255)
        self.rectangles = [
            {"id": 1, "rect": pygame.Rect(105, 465, 397, 42)},
            {"id": 2, "rect": pygame.Rect(502, 465, 395, 42)}
        ]
        for rect in self.rectangles:
            pygame.draw.rect(self.display, WHITE, rect["rect"], 1)

    def load_assets(self):
        self.assets_dir = os.path.join("assets")
        self.states_dir = os.path.join(self.assets_dir, "states")
        self.font_dir = os.path.join(self.assets_dir, "font")
        self.font = pygame.font.Font(os.path.join(self.font_dir, "PressStart2P-Regular.ttf"), 20)
        # self.gif_obj = gif.load(os.path.join(self.states_dir, "win.gif")) # without secret
        self.gif_obj = gif.load(os.path.join(self.states_dir, "win_1.gif"))
