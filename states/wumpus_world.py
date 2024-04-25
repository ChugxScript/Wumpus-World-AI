import os
import pygame
import gif_pygame as gif
import random

class WumpusWorld():
    def __init__(self, display, gameStateManager, current_player, current_world_size):
        self.display = display
        self.gameStateManager = gameStateManager
        self.current_player = current_player
        self.current_world_size = current_world_size
        self.FPS = 60
        self.clock = pygame.time.Clock()        

    def run(self):
        self.load_assets()
        self.set_player()
        self.set_world_size()    
        self.draw_board()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            
            
            self.display.fill((255, 255, 255))
            self.gif_obj.render(self.display, (0, 0)) # gif background
            self.display.blit(self.board_surface, self.board_coord) # board
            
            pygame.display.flip()
            self.clock.tick(self.FPS)
    
    def set_player(self):
        if self.current_player == 'select_game_mode_1':
            # set player to AI
            pass
        elif self.current_player == 'select_game_mode_2':
            # set player to user
            pass
        else:
            print(f"Invalid self.current_player: {self.current_player}")
    
    def set_world_size(self):
        if self.current_world_size == 'select_world_size_1':
            self.board_size = 4
            self.cell_size = 125
            self.board_coord = (80, 50)
            self.probability_blue_cells = 0.6 # 0.2 is too low
            self.red_cells = 1
            self.yellow_cells = 1
        elif self.current_world_size == 'select_world_size_2':
            self.board_size = 6
            self.cell_size = 83
            self.board_coord = (78, 50)
            self.probability_blue_cells = 0.7
            self.red_cells = 2
            self.yellow_cells = 1
        elif self.current_world_size == 'select_world_size_3':
            self.board_size = 8
            self.cell_size = 62
            self.board_coord = (82, 50)
            self.probability_blue_cells = 1
            self.red_cells = 3
            self.yellow_cells = 2
        elif self.current_world_size == 'select_world_size_4':
            self.board_size = 10
            self.cell_size = 50
            self.board_coord = (82, 50)
            self.probability_blue_cells = 2
            self.red_cells = 6
            self.yellow_cells = 3
        else:
            print(f"Invalid self.current_world_size: {self.current_world_size}")

    def draw_board(self):
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        self.board_surface = pygame.Surface((self.board_width, self.board_height))
        
        # the first square is the starting position therefore the color is white
        # the number of blue, red, and yellow will depend on the size of board_size
        # the number of red and yellow cells must be satisfy
        self.cells = []
        for y in range(self.board_size):
            row = []
            for x in range(self.board_size):
                row.append(0)  # 0 represents white cells
            self.cells.append(row)
        
        # check if there is a path from first cell to the yellow cells in the board where the path must not go through the blue or red cells
        # if there are no path from first cell to the yellow cells then make a random path from first cell to the yellow cells
        # by making the random path cells white
        # if the random path is valid then print the baord else undo the generated random path and do random path again

        # Set the starting position
        start_x, start_y = 0, 0
        self.cells[start_y][start_x] = 1  # 1 represents the starting position

        # Place blue cells
        for _ in range(int(self.probability_blue_cells * self.board_size)):
            while True:
                x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if self.cells[y][x] == 0 and not (y == 0 and x == 1) and not (y == 1 and x == 0):
                    self.cells[y][x] = 2  # 2 represents blue cells
                    break

        # Place red cells
        red_cells_placed = 0
        while red_cells_placed < self.red_cells:
            while True:
                x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                # Only place if cell is empty
                if self.cells[y][x] == 0 and not (y == 0 and x == 1) and not (y == 1 and x == 0):  
                    self.cells[y][x] = 3  # 3 represents red cells
                    red_cells_placed += 1
                    break

        # Place yellow cells
        for _ in range(self.yellow_cells):
            # Ensure yellow cells are not too close to the starting position
            while True:
                x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if abs(x - start_x) + abs(y - start_y) > 2 and self.cells[y][x] == 0:  # Only place if cell is empty and not too close to the starting position
                    self.cells[y][x] = 4  # 4 represents yellow cells
                    break

        # Check if there's a path from the starting cell to each yellow cell
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.cells[y][x] == 4:
                    if not self.is_valid_path(start_x, start_y, x, y):
                        self.cells = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
                        self.cells[start_y][start_x] = 1
                        self.draw_board()  # Restart drawing board if path is not valid
                        return
        
        self.draw_cell()

    def is_valid_path(self, start_x, start_y, end_x, end_y):
        visited = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]

        # A DFS function to check if there is a path from start to end
        def dfs(x, y):
            if x < 0 or x >= self.board_size or y < 0 or y >= self.board_size or self.cells[y][x] in [2, 3] or visited[y][x]:
                return False
            visited[y][x] = True
            if x == end_x and y == end_y:
                return True
            if dfs(x + 1, y) or dfs(x - 1, y) or dfs(x, y + 1) or dfs(x, y - 1):
                return True
            return False

        return dfs(start_x, start_y)
    
    def draw_cell(self):
        for y in range(self.board_size):
            for x in range(self.board_size):
                self.safe_cell = pygame.image.load(os.path.join(self.tile_status, "safe_tile.png"))
                self.safe_cell = pygame.transform.scale(self.safe_cell, (self.cell_size, self.cell_size))
                self.board_surface.blit(self.safe_cell, (x * self.cell_size, y * self.cell_size))
                
                if self.cells[y][x] == 1: # Starting position
                    self.start_cell = pygame.image.load(os.path.join(self.tile_status, "start_tile.png"))
                    self.start_cell = pygame.transform.scale(self.start_cell, (self.cell_size, self.cell_size))
                    self.board_surface.blit(self.start_cell, (x * self.cell_size, y * self.cell_size))

                elif self.cells[y][x] == 2:  # Blue cell
                    self.pit_cell = pygame.image.load(os.path.join(self.images_dir, "pit.png"))
                    self.pit_cell = pygame.transform.scale(self.pit_cell, (self.cell_size, self.cell_size))
                    self.board_surface.blit(self.pit_cell, (x * self.cell_size, y * self.cell_size))

                elif self.cells[y][x] == 3:  # Red cell
                    self.wumpus_cell = pygame.image.load(os.path.join(self.images_dir, "wumpus.png"))
                    self.wumpus_cell = pygame.transform.scale(self.wumpus_cell, (self.cell_size, self.cell_size))
                    self.board_surface.blit(self.wumpus_cell, (x * self.cell_size, y * self.cell_size))

                elif self.cells[y][x] == 4:  # Yellow cell
                    self.gold_cell = pygame.image.load(os.path.join(self.images_dir, "gold.png"))
                    self.gold_cell = pygame.transform.scale(self.gold_cell, (self.cell_size, self.cell_size))
                    self.board_surface.blit(self.gold_cell, (x * self.cell_size, y * self.cell_size))
                
                else:
                    pit_adjacent = self.adjacent_cell(y + 1, x, 2) or self.adjacent_cell(y - 1, x, 2) or self.adjacent_cell(y, x + 1, 2) or self.adjacent_cell(y, x - 1, 2)
                    wumpus_adjacent = self.adjacent_cell(y + 1, x, 3) or self.adjacent_cell(y - 1, x, 3) or self.adjacent_cell(y, x + 1, 3) or self.adjacent_cell(y, x - 1, 3)
                    gold_adjacent = self.adjacent_cell(y + 1, x, 4) or self.adjacent_cell(y - 1, x, 4) or self.adjacent_cell(y, x + 1, 4) or self.adjacent_cell(y, x - 1, 4)

                    if pit_adjacent and wumpus_adjacent and gold_adjacent:
                        self.stench_breeze_glitter_cell = pygame.image.load(os.path.join(self.tile_status, "stench_breeze_glitter_tile.png"))
                        self.stench_breeze_glitter_cell = pygame.transform.scale(self.stench_breeze_glitter_cell, (self.cell_size, self.cell_size))
                        self.board_surface.blit(self.stench_breeze_glitter_cell, (x * self.cell_size, y * self.cell_size))
                    
                    elif pit_adjacent and wumpus_adjacent:
                        self.stench_breeze_cell = pygame.image.load(os.path.join(self.tile_status, "stench_breeze_tile.png"))
                        self.stench_breeze_cell = pygame.transform.scale(self.stench_breeze_cell, (self.cell_size, self.cell_size))
                        self.board_surface.blit(self.stench_breeze_cell, (x * self.cell_size, y * self.cell_size))

                    elif pit_adjacent and gold_adjacent:
                        self.breeze_glitter_cell = pygame.image.load(os.path.join(self.tile_status, "breeze_glitter_tile.png"))
                        self.breeze_glitter_cell = pygame.transform.scale(self.breeze_glitter_cell, (self.cell_size, self.cell_size))
                        self.board_surface.blit(self.breeze_glitter_cell, (x * self.cell_size, y * self.cell_size))

                    elif wumpus_adjacent and gold_adjacent:
                        self.stench_glitter_cell = pygame.image.load(os.path.join(self.tile_status, "stench_glitter_tile.png"))
                        self.stench_glitter_cell = pygame.transform.scale(self.stench_glitter_cell, (self.cell_size, self.cell_size))
                        self.board_surface.blit(self.stench_glitter_cell, (x * self.cell_size, y * self.cell_size))

                    elif pit_adjacent:
                        self.breeze_cell = pygame.image.load(os.path.join(self.tile_status, "breeze_tile.png"))
                        self.breeze_cell = pygame.transform.scale(self.breeze_cell, (self.cell_size, self.cell_size))
                        self.board_surface.blit(self.breeze_cell, (x * self.cell_size, y * self.cell_size))

                    elif wumpus_adjacent:
                        self.stench_cell = pygame.image.load(os.path.join(self.tile_status, "stench_tile.png"))
                        self.stench_cell = pygame.transform.scale(self.stench_cell, (self.cell_size, self.cell_size))
                        self.board_surface.blit(self.stench_cell, (x * self.cell_size, y * self.cell_size))

                    elif gold_adjacent:
                        self.glitter_cell = pygame.image.load(os.path.join(self.tile_status, "glitter_tile.png"))
                        self.glitter_cell = pygame.transform.scale(self.glitter_cell, (self.cell_size, self.cell_size))
                        self.board_surface.blit(self.glitter_cell, (x * self.cell_size, y * self.cell_size))
    
    def adjacent_cell(self, y, x, target_color):
        if y < 0 or y >= self.board_size or x < 0 or x >= self.board_size:
            return False
        return self.cells[y][x] == target_color

    def load_assets(self):
        self.assets_dir = os.path.join("assets")
        self.states_dir = os.path.join(self.assets_dir, "states")
        self.board_dir = os.path.join(self.assets_dir, "board")
        self.images_dir = os.path.join(self.board_dir, "img")
        self.tile_status = os.path.join(self.images_dir, "tile_status")
        self.gif_obj = gif.load(os.path.join(self.states_dir, "board.gif"))


# remove it later
from game_state_manager import GameStateManager
if __name__=='__main__':
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    game_state_manager = GameStateManager('wumpus')
    wumpus = WumpusWorld(screen, game_state_manager, 'select_game_mode_1', 'select_world_size_4')
    states = {
        'wumpus': wumpus
    }
    states[game_state_manager.get_state()].run()