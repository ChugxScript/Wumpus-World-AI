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
            self.gif_obj.render(self.display, (0, 0))
            self.display.blit(self.board_surface, self.board_coord)
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
        print("--- 1")
        
        # the first square is the starting position therefore the color is white
        # the number of blue, red, and yellow will depend on the size of board_size
        # the number of red and yellow cells must be satisfy
        self.cells = []
        for y in range(self.board_size):
            row = []
            for x in range(self.board_size):
                row.append(0)  # 0 represents white cells
            self.cells.append(row)
        
        print("--- 2")
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
        print("--- 3")

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
        print("--- 4")

        # Place yellow cells
        for _ in range(self.yellow_cells):
            # Ensure yellow cells are not too close to the starting position
            while True:
                x, y = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if abs(x - start_x) + abs(y - start_y) > 2 and self.cells[y][x] == 0:  # Only place if cell is empty and not too close to the starting position
                    self.cells[y][x] = 4  # 4 represents yellow cells
                    break
        print("--- 5")

        # Check if there's a path from the starting cell to each yellow cell
        for y in range(self.board_size):
            for x in range(self.board_size):
                if self.cells[y][x] == 4:
                    if not self.is_valid_path(start_x, start_y, x, y):
                        self.cells = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
                        self.cells[start_y][start_x] = 1
                        self.draw_board()  # Restart drawing board if path is not valid
                        return
        print("--- 6")

        # after having a valid path 
        # put black cell if the cell is the starting cell
        # put green cell if the cell is adjacent to blue cell
        # put orange cell if the cell is adjacent to red cell
        # put purple cell if the cell is adjacent to yellow cell
        # put pink cell if the cell is adjacent to blue and red cell
        # put gray cell if the cell is adjacent to blue and yellow cell
        # put Turquoise cell if the cell is adjacent to red and yellow cell
        # put brown cell if the cell is adjacent to blue and red and yellow cell
        # put Cyan cell if the cell is not adjacent to red, blue, and yellow cell

        # Draw cells on the board
        # for y in range(self.board_size):
        #     for x in range(self.board_size):
        #         color = (255, 255, 255)  # Default color is white
        #         if self.cells[y][x] == 1:  # Starting position
        #             color = (0, 0, 0)
        #         elif self.cells[y][x] == 2:  # Blue cell
        #             color = (0, 0, 255)
        #         elif self.cells[y][x] == 3:  # Red cell
        #             color = (255, 0, 0)
        #         elif self.cells[y][x] == 4:  # Yellow cell
        #             color = (255, 255, 0)
        #         pygame.draw.rect(self.board_surface, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

        for y in range(self.board_size):
            for x in range(self.board_size):
                color = (255, 255, 255)  # Default color is white
                adjacent_colors = set()
                if self.cells[y][x] == 1:  # Starting position
                    color = (0, 0, 0)  # Black
                elif self.cells[y][x] == 2:  # Blue cell
                    color = (0, 0, 255)
                elif self.cells[y][x] == 3:  # Red cell
                    color = (255, 0, 0)
                elif self.cells[y][x] == 4:  # Yellow cell
                    color = (255, 255, 0)

                # Check adjacent cells
                if y > 0:
                    adjacent_colors.add(self.cells[y - 1][x])
                if y < self.board_size - 1:
                    adjacent_colors.add(self.cells[y + 1][x])
                if x > 0:
                    adjacent_colors.add(self.cells[y][x - 1])
                if x < self.board_size - 1:
                    adjacent_colors.add(self.cells[y][x + 1])

                if 2 in adjacent_colors and 3 in adjacent_colors:
                    color = (255, 192, 203)  # Pink
                elif 2 in adjacent_colors and 4 in adjacent_colors:
                    color = (128, 128, 128)  # Gray
                elif 3 in adjacent_colors and 4 in adjacent_colors:
                    color = (64, 224, 208)  # Turquoise
                elif 2 in adjacent_colors and 3 in adjacent_colors and 4 in adjacent_colors:
                    color = (165, 42, 42)  # Brown
                elif 2 in adjacent_colors:
                    color = (0, 128, 0)  # Green
                elif 3 in adjacent_colors:
                    color = (255, 165, 0)  # Orange
                elif 4 in adjacent_colors:
                    color = (128, 0, 128)  # Purple
                else:
                    color = (255, 255, 255)  # white

                pygame.draw.rect(self.board_surface, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))
        print("--- 7")

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

    def load_assets(self):
        self.assets_dir = os.path.join("assets")
        self.states_dir = os.path.join(self.assets_dir, "states")
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