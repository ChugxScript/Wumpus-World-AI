import pygame
import os
from states.title import Title
from states.game_state_manager import GameStateManager

class Game():
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 1000
        self.SCREEN_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        
        self.game_state_manager = GameStateManager('title')
        self.title = Title(self.screen, self.game_state_manager)

        self.states = {
            'title': self.title,
        }

    def run(self):
        pygame.display.set_caption("Wumpus World")
        icon = pygame.image.load(os.path.join('assets', 'board', 'img', 'GameIcon1.png'))
        pygame.display.set_icon(icon)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self.states[self.game_state_manager.get_state()].run()
            
            pygame.display.flip()
            self.clock.tick(self.FPS)


if __name__ == "__main__":
    g = Game()
    g.run()