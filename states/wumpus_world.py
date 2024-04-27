import os
import pygame
import gif_pygame as gif
import random
from win import Win
from lose import Lose

class WumpusWorld():
    def __init__(self, display, gameStateManager, current_player, current_world_size):
        pygame.init()
        self.display = display
        self.gameStateManager = gameStateManager
        self.current_player = current_player
        self.current_world_size = current_world_size
        self.FPS = 60
        self.WHITE = (255, 255, 255)
        self.clock = pygame.time.Clock() 

        self.player_moves = {}
        # self.player_moves will keep track of the moves that the player took
        # if the player click 'd' means left and the coord of that is (0, 1)
        # then we store the move to the dictionary and the status of that cell
        # example inputs are
        # {
        #     (0, 0): 'start_cell',
        #     (0, 1): 'safe_cell',
        #     (0, 2): 'pit_cell',
        #     (0, 3): 'wumpus_cell',
        #     (1, 0): 'gold_cell',
        #     (1, 1): 'stench_breeze_glitter_cell',
        #     (1, 2): 'stench_breeze_cell',
        #     (1, 3): 'breeze_glitter_cell',
        #     (2, 0): 'stench_glitter_cell',
        #     (2, 1): 'breeze_cell',
        #     (2, 2): 'stench_cell',
        #     (2, 3): 'glitter_cell',
        #     # and so on...
        # }

        # initially the player is facing right
        self.facing_in = {
            'right': True,
            'left': False,
            'above': False,
            'below': False,
        }
        self.curr_position = [0, 0]
        self.player_score = 0
        self.action_minus_score = 0
        self.still_gold = False

        # !important
        # 0 means safe cell
        # 1 means starting cell
        # 2 means pit cell
        # 3 means wumpus cell
        # 4 means gold cell
        # 5 means cell is adjacent to pit cell
        # 6 means cell is adjacent to wumpus cell
        # 7 means cell is adjacent to gold cell
        # 8 means cell is adjacent to pit and wumpus cell
        # 9 means cell is adjacent to pit and gold cell
        # 10 means cell is adjacent to wumpus and gold cell
        # 11 means cell is adjacent to pit, wumpus, and gold cell

        self.is_win_lose = False
        self.win = Win(self.display, self.gameStateManager)
        self.lose = Lose(self.display, self.gameStateManager)

    def run(self):
        self.load_assets()
        self.set_world_size()  
        self.set_player()  
        self.draw_board()

        # put player_avatar on top of the starting cell
        self.update_player_avatar_position(0, 0)
        self.temp = self.check_valid_move(0, 0)
        self.load_skill_gold_()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                
                if self.is_player:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_w:
                            self.player_move_to('w')
                        if event.key == pygame.K_a:
                            self.player_move_to('a')
                        if event.key == pygame.K_s:
                            self.player_move_to('s')
                        if event.key == pygame.K_d:
                            self.player_move_to('d')
                        if event.key == pygame.K_SPACE:
                            self.player_move_to('space')
            
            self.display.fill((255, 255, 255))
            self.gif_obj.render(self.display, (0, 0)) # gif background
            self.display.blit(self.board_surface, self.board_coord) # board
            self.display.blit(self.player_avatar, self.player_avatar_rect) # player
            self.display.blit(self.cell_status, (725, 268)) # tile status
            self.display.blit(self.skill_text, (900, 115))
            self.display.blit(self.yellow_cell_text, (900, 180))

            pygame.display.flip()
            if self.is_win_lose:
                self.gameStateManager.get_state().run(self.player_score)
            self.clock.tick(self.FPS)
    
    def set_player(self):
        if self.current_player == 'select_game_mode_1':
            # set player to AI
            self.is_player = False
            self.is_AI = True
        elif self.current_player == 'select_game_mode_2':
            # set player to user
            self.is_player = True
            self.is_AI = False
        else:
            print(f"Invalid self.current_player: {self.current_player}")
        
        # load player avatar
        self.player_avatar = pygame.image.load(os.path.join(self.images_dir, "playerr.png"))
        self.player_avatar = pygame.transform.scale(self.player_avatar, (self.cell_size, self.cell_size))

    def set_world_size(self):
        if self.current_world_size == 'select_world_size_1':
            self.board_size = 4
            self.cell_size = 125
            self.board_coord = (80, 50)
            self.probability_blue_cells = 0.6 # 0.2 is too low
            self.red_cells = 1
            self.yellow_cells = 1
            self.skill = 1
        elif self.current_world_size == 'select_world_size_2':
            self.board_size = 6
            self.cell_size = 83
            self.board_coord = (78, 50)
            self.probability_blue_cells = 0.7
            self.red_cells = 3
            self.yellow_cells = 1
            self.skill = 2
        elif self.current_world_size == 'select_world_size_3':
            self.board_size = 8
            self.cell_size = 62
            self.board_coord = (82, 50)
            self.probability_blue_cells = 1
            self.red_cells = 6
            self.yellow_cells = 2
            self.skill = 3
        elif self.current_world_size == 'select_world_size_4':
            self.board_size = 10
            self.cell_size = 50
            self.board_coord = (82, 50)
            self.probability_blue_cells = 2
            self.red_cells = 9
            self.yellow_cells = 3
            self.skill = 5
        else:
            print(f"Invalid self.current_world_size: {self.current_world_size}")

    def draw_board(self):
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        self.board_surface = pygame.Surface((self.board_width, self.board_height))
        
        # the first square is the starting position therefore the cell is start cell
        # the number of pit, wumpus, and gold will depend on the size of board_size
        # the number of wumpus and gold cells must be satisfy
        self.cells = []
        for row in range(self.board_size):
            row = []
            for col in range(self.board_size):
                row.append(0)  # 0 represents safe cells
            self.cells.append(row)
        
        # check if there is a path from first cell to the gold cells in the board where the path must not go through the pit or wumpus cells
        # if there are no path from first cell to the gold cells then make a random path from first cell to the gold cells
        # by making the random path cells safe cell
        # if the random path is valid then print the baord else undo the generated random path and do random path again

        # Set the starting position
        start_row, start_col = 0, 0
        self.cells[start_row][start_col] = 1  # 1 represents the starting position

        # Place pit cells
        for _ in range(int(self.probability_blue_cells * self.board_size)):
            while True:
                row, col = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if self.cells[row][col] == 0 and not (row == 0 and col == 1) and not (row == 1 and col == 0):
                    self.cells[row][col] = 2  # 2 represents pit cells
                    break

        # Place wumpus cells
        red_cells_placed = 0
        while red_cells_placed < self.red_cells:
            while True:
                row, col = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                # Only place if cell is empty
                if self.cells[row][col] == 0 and not (row == 0 and col == 1) and not (row == 1 and col == 0):  
                    self.cells[row][col] = 3  # 3 represents wumpus cells
                    red_cells_placed += 1
                    break

        # Place gold cells
        for _ in range(self.yellow_cells):
            # Ensure yellow cells are not too close to the starting position
            while True:
                row, col = random.randint(0, self.board_size - 1), random.randint(0, self.board_size - 1)
                if abs(row - start_row) + abs(col - start_col) > 2 and self.cells[row][col] == 0:  # Only place if cell is empty and not too close to the starting position
                    self.cells[row][col] = 4  # 4 represents gold cells
                    break

        # Check if there's a path from the starting cell to each gold cell
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.cells[row][col] == 4:
                    if not self.is_valid_path(start_row, start_col, row, col):
                        self.cells = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
                        self.cells[start_row][start_col] = 1
                        self.draw_board()  # Restart drawing board if path is not valid
                        return
        
        self.draw_cell()

    def is_valid_path(self, start_row, start_col, end_row, end_col):
        visited = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]

        # A DFS function to check if there is a path from start to end
        def dfs(row, col):
            if  row < 0 or row >= self.board_size or col < 0 or col >= self.board_size or self.cells[row][col] in [2, 3] or visited[row][col]:
                return False
            visited[row][col] = True
            if row == end_row and col == end_col:
                return True
            if dfs(row + 1, col) or dfs(row - 1, col) or dfs(row, col + 1) or dfs(row, col - 1):
                return True
            return False

        return dfs(start_row, start_col)
    
    def draw_cell(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.safe_cell = pygame.image.load(os.path.join(self.tile_status, "safe_tile.png"))
                self.safe_cell = pygame.transform.scale(self.safe_cell, (self.cell_size, self.cell_size))
                self.board_surface.blit(self.safe_cell, (col * self.cell_size, row * self.cell_size))
                
                if self.cells[row][col] == 1: # Starting position
                    self.start_cell = pygame.image.load(os.path.join(self.tile_status, "start_tile.png"))
                    self.start_cell = pygame.transform.scale(self.start_cell, (self.cell_size, self.cell_size))
                    self.board_surface.blit(self.start_cell, (col * self.cell_size, row * self.cell_size))

                elif self.cells[row][col] == 2:  # Blue cell
                    self.pit_cell = pygame.image.load(os.path.join(self.images_dir, "pit.png"))
                    self.pit_cell = pygame.transform.scale(self.pit_cell, (self.cell_size, self.cell_size))
                    self.board_surface.blit(self.pit_cell, (col * self.cell_size, row * self.cell_size))

                elif self.cells[row][col] == 3:  # Red cell
                    self.wumpus_cell = pygame.image.load(os.path.join(self.images_dir, "wumpus.png"))
                    self.wumpus_cell = pygame.transform.scale(self.wumpus_cell, (self.cell_size, self.cell_size))
                    self.board_surface.blit(self.wumpus_cell, (col * self.cell_size, row * self.cell_size))

                elif self.cells[row][col] == 4:  # Yellow cell
                    self.gold_cell = pygame.image.load(os.path.join(self.images_dir, "gold.png"))
                    self.gold_cell = pygame.transform.scale(self.gold_cell, (self.cell_size, self.cell_size))
                    self.board_surface.blit(self.gold_cell, (col * self.cell_size, row * self.cell_size))
                
                else:
                    pit_adjacent = self.adjacent_cell(row + 1, col, 2) or self.adjacent_cell(row - 1, col, 2) or self.adjacent_cell(row, col + 1, 2) or self.adjacent_cell(row, col - 1, 2)
                    wumpus_adjacent = self.adjacent_cell(row + 1, col, 3) or self.adjacent_cell(row - 1, col, 3) or self.adjacent_cell(row, col + 1, 3) or self.adjacent_cell(row, col - 1, 3)
                    gold_adjacent = self.adjacent_cell(row + 1, col, 4) or self.adjacent_cell(row - 1, col, 4) or self.adjacent_cell(row, col + 1, 4) or self.adjacent_cell(row, col - 1, 4)

                    if pit_adjacent:
                        self.cells[row][col] = 5
                        self.breeze_cell = pygame.image.load(os.path.join(self.tile_status, "breeze_tile.png"))
                        self.breeze_cell = pygame.transform.scale(self.breeze_cell, (self.cell_size, self.cell_size))
                        self.board_surface.blit(self.breeze_cell, (col * self.cell_size, row * self.cell_size))

                    if wumpus_adjacent:
                        if self.cells[row][col] != 5:
                            self.stench_cell = pygame.image.load(os.path.join(self.tile_status, "stench_tile.png"))
                            self.stench_cell = pygame.transform.scale(self.stench_cell, (self.cell_size, self.cell_size))
                            self.board_surface.blit(self.stench_cell, (col * self.cell_size, row * self.cell_size))
                            self.cells[row][col] = 6
                        else:
                            self.stench_breeze_cell = pygame.image.load(os.path.join(self.tile_status, "stench_breeze_tile.png"))
                            self.stench_breeze_cell = pygame.transform.scale(self.stench_breeze_cell, (self.cell_size, self.cell_size))
                            self.board_surface.blit(self.stench_breeze_cell, (col * self.cell_size, row * self.cell_size))
                            self.cells[row][col] = 8
                        

                    if gold_adjacent:
                        if self.cells[row][col] != 5 and self.cells[row][col] != 6:
                            self.glitter_cell = pygame.image.load(os.path.join(self.tile_status, "glitter_tile.png"))
                            self.glitter_cell = pygame.transform.scale(self.glitter_cell, (self.cell_size, self.cell_size))
                            self.board_surface.blit(self.glitter_cell, (col * self.cell_size, row * self.cell_size))
                            self.cells[row][col] = 7

                        elif self.cells[row][col] == 5:
                            self.breeze_glitter_cell = pygame.image.load(os.path.join(self.tile_status, "breeze_glitter_tile.png"))
                            self.breeze_glitter_cell = pygame.transform.scale(self.breeze_glitter_cell, (self.cell_size, self.cell_size))
                            self.board_surface.blit(self.breeze_glitter_cell, (col * self.cell_size, row * self.cell_size))
                            self.cells[row][col] = 9

                        elif self.cells[row][col] == 6:
                            self.stench_glitter_cell = pygame.image.load(os.path.join(self.tile_status, "stench_glitter_tile.png"))
                            self.stench_glitter_cell = pygame.transform.scale(self.stench_glitter_cell, (self.cell_size, self.cell_size))
                            self.board_surface.blit(self.stench_glitter_cell, (col * self.cell_size, row * self.cell_size))
                            self.cells[row][col] = 10

                        elif self.cells[row][col] == 8:
                            self.stench_breeze_glitter_cell = pygame.image.load(os.path.join(self.tile_status, "stench_breeze_glitter_tile.png"))
                            self.stench_breeze_glitter_cell = pygame.transform.scale(self.stench_breeze_glitter_cell, (self.cell_size, self.cell_size))
                            self.board_surface.blit(self.stench_breeze_glitter_cell, (col * self.cell_size, row * self.cell_size))
                            self.cells[row][col] = 11
    
    def adjacent_cell(self, row, col, target_color):
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return False
        return self.cells[row][col] == target_color
    
    def player_move_to(self, key):
        curr_row, curr_col = self.curr_position[0], self.curr_position[1]
        new_row, new_col = curr_row, curr_col  
        
        if key == 'w':
            if self.facing_in['above']:
                new_row -= 1
                self.action_minus_score += 1
            else:
                # Rotate or flip the player_avatar based on the current direction it's facing
                if self.facing_in['left']:
                    self.player_avatar = pygame.transform.rotate(self.player_avatar, -90)
                if self.facing_in['right']:
                    self.player_avatar = pygame.transform.rotate(self.player_avatar, 90)
                if self.facing_in['below']:
                    self.player_avatar = pygame.transform.flip(self.player_avatar, False, True)

                # Then set 'above' to True
                self.facing_in = {'above': True, 'below': False, 'left': False, 'right': False}

        elif key == 's':
            if self.facing_in['below']:
                new_row += 1
                self.action_minus_score += 1
            else:
                # Rotate or flip the player_avatar based on the current direction it's facing
                if self.facing_in['left']:
                    self.player_avatar = pygame.transform.rotate(self.player_avatar, 90)
                if self.facing_in['right']:
                    self.player_avatar = pygame.transform.rotate(self.player_avatar, -90)
                if self.facing_in['above']:
                    self.player_avatar = pygame.transform.flip(self.player_avatar, False, True)

                self.facing_in = {'above': False, 'below': True, 'left': False, 'right': False}

        elif key == 'a':
            if self.facing_in['left']:
                new_col -= 1
                self.action_minus_score += 1
            else:
                # Rotate or flip the player_avatar based on the current direction it's facing
                if self.facing_in['above']:
                    self.player_avatar = pygame.transform.rotate(self.player_avatar, 90)
                if self.facing_in['below']:
                    self.player_avatar = pygame.transform.rotate(self.player_avatar, -90)
                if self.facing_in['right']:
                    self.player_avatar = pygame.transform.flip(self.player_avatar, True, False)

                self.facing_in = {'above': False, 'below': False, 'left': True, 'right': False}
        
        elif key == 'd':
            if self.facing_in['right']:
                new_col += 1
                self.action_minus_score += 1
            else:
                # Rotate or flip the player_avatar based on the current direction it's facing
                if self.facing_in['above']:
                    self.player_avatar = pygame.transform.rotate(self.player_avatar, -90)
                if self.facing_in['below']:
                    self.player_avatar = pygame.transform.rotate(self.player_avatar, 90)
                if self.facing_in['left']:
                    self.player_avatar = pygame.transform.flip(self.player_avatar, True, False)

                self.facing_in = {'above': False, 'below': False, 'left': False, 'right': True}

        elif key == 'space':
            if self.cells[curr_row][curr_col] == 1:
                # start cell
                if self.yellow_cells == 0:
                    # climb out
                    self.player_score -= self.action_minus_score
                    print(f"climb self.player_score: {self.player_score}")
                    self.gameStateManager.set_state(self.win)
                    self.is_win_lose = True
                    self.still_gold = False
                else:
                    self.still_gold = True

            elif self.cells[curr_row][curr_col] == 4:
                # grab the gold
                self.cells[curr_row][curr_col] = 0
                self.draw_cell()
                self.yellow_cells -= 1
                self.player_score += 1000
                print(f"gold self.player_score: {self.player_score}")
                self.load_skill_gold_()

            elif self.skill != 0:
                # fire the spirit ball !!!!
                self.spirit_ball = pygame.image.load(os.path.join(self.images_dir, "skill.png"))
                self.spirit_ball = pygame.transform.scale(self.spirit_ball, (self.cell_size, self.cell_size))
                
                s_ball_row = curr_row
                s_ball_col = curr_col 
                self.action_minus_score += 10
                self.skill -= 1
                self.wumpus_hit = False
                if self.facing_in['above']:
                    while s_ball_row != 0:
                        s_ball_row -= 1
                        self.fire_spirit_ball(s_ball_row, s_ball_col)
                        self.display.blit(self.spirit_ball, self.spirit_ball_rect)
                        pygame.display.flip()
                        pygame.time.wait(50)
                        if self.cells[s_ball_row][s_ball_col] == 3:
                            self.wumpus_hit = True
                            break
                        
                if self.facing_in['below']:
                    while s_ball_row != self.board_size - 1:
                        s_ball_row += 1
                        self.fire_spirit_ball(s_ball_row, s_ball_col)
                        self.display.blit(self.spirit_ball, self.spirit_ball_rect)
                        pygame.display.flip()
                        pygame.time.wait(50)
                        if self.cells[s_ball_row][s_ball_col] == 3:
                            self.wumpus_hit = True
                            break
                        
                if self.facing_in['left']:
                    while s_ball_col != 0:
                        s_ball_col -= 1
                        self.fire_spirit_ball(s_ball_row, s_ball_col)
                        self.display.blit(self.spirit_ball, self.spirit_ball_rect)
                        pygame.display.flip()
                        pygame.time.wait(50)
                        if self.cells[s_ball_row][s_ball_col] == 3:
                            self.wumpus_hit = True
                            break
                        
                if self.facing_in['right']:
                    while s_ball_col != self.board_size - 1:
                        s_ball_col += 1
                        self.fire_spirit_ball(s_ball_row, s_ball_col)
                        self.display.blit(self.spirit_ball, self.spirit_ball_rect)
                        pygame.display.flip()
                        pygame.time.wait(50)
                        if self.cells[s_ball_row][s_ball_col] == 3:
                            self.wumpus_hit = True
                            break
                        
                if self.wumpus_hit:
                    self.display_time = pygame.time.get_ticks() + 3000
                    self.scream = gif.load(os.path.join(self.gif_dir, "scream.gif"))
                    while self.wumpus_hit:
                        self.scream.render(self.display, (82, 50))
                        pygame.display.flip()
                        if pygame.time.get_ticks() > self.display_time:
                            self.wumpus_hit = False
                    
                    # use this instead if the program is crashing
                    # self.scream = pygame.image.load(os.path.join(self.images_dir, "scream.png"))
                    # self.display.blit(self.scream, (82, 50))
                    # pygame.display.flip()
                    # pygame.time.wait(3000)
                    self.cells[s_ball_row][s_ball_col] = 0
                    self.draw_cell()

                self.load_skill_gold_()
            
        # Check if the new position is valid
        if self.check_valid_move(new_row, new_col):
            self.curr_position[0] = new_row
            self.curr_position[1] = new_col
            
            # store the cell and its status
            self.player_moves[(new_row, new_col)] = self.cells[new_row][new_col]
            print(f"\n>> self.player_moves: {self.player_moves}")
            self.update_player_avatar_position(new_row, new_col)

            # check if the current cell is a pit or a wumpus
            if self.cells[new_row][new_col] == 2:
                self.action_minus_score += 1000
                self.player_score -= self.action_minus_score
                print(f"pit self.player_score: {self.player_score}")
                self.gameStateManager.set_state(self.lose)
                self.is_win_lose = True

            if self.cells[new_row][new_col] == 3:
                self.action_minus_score += 1000
                self.player_score -= self.action_minus_score
                print(f"wumpus self.player_score: {self.player_score}")
                self.gameStateManager.set_state(self.lose)
                self.is_win_lose = True

    def check_valid_move(self, row, col):
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "bump_tile.png"))
            self.cell_status = pygame.transform.scale(self.cell_status, (200, 200))
            return False
        
        # check what value of y and x in self.cells
        self.curr_cell_value = self.cells[row][col]
        
        if self.curr_cell_value == 0:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "safe_tile.png"))
        elif self.curr_cell_value == 1:
            if self.still_gold:
                # self.cell_status = pygame.image.load(os.path.join(self.tile_status, "still_golds_1.png")) # this one is formal
                self.cell_status = pygame.image.load(os.path.join(self.tile_status, "still_golds_2.png"))
                self.still_gold = False
            else: self.cell_status = pygame.image.load(os.path.join(self.tile_status, "start_tile.png"))
        elif self.curr_cell_value == 2:
            self.cell_status = pygame.image.load(os.path.join(self.images_dir, "pit.png"))
        elif self.curr_cell_value == 3:
            self.cell_status = pygame.image.load(os.path.join(self.images_dir, "wumpus.png"))
        elif self.curr_cell_value == 4:
            self.cell_status = pygame.image.load(os.path.join(self.images_dir, "gold.png"))
        elif self.curr_cell_value == 5:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "breeze_tile.png"))
        elif self.curr_cell_value == 6:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "stench_tile.png"))
        elif self.curr_cell_value == 7:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "glitter_tile.png"))
        elif self.curr_cell_value == 8:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "stench_breeze_tile.png"))
        elif self.curr_cell_value == 9:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "breeze_glitter_tile.png"))
        elif self.curr_cell_value == 10:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "stench_glitter_tile.png"))
        elif self.curr_cell_value == 11:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "stench_breeze_glitter_tile.png"))

        self.cell_status = pygame.transform.scale(self.cell_status, (200, 200))
        return True

    def update_player_avatar_position(self, new_row, new_col):
        # Calculate the new position of the player_avatar
        player_avatar_x = self.board_coord[0] + new_col * self.cell_size
        player_avatar_y = self.board_coord[1] + new_row * self.cell_size
        
        # Update the player_avatar position
        self.player_avatar_rect = self.player_avatar.get_rect(topleft=(player_avatar_x, player_avatar_y))

    def fire_spirit_ball(self, new_row, new_col):
        spirit_ball_x = self.board_coord[0] + new_col * self.cell_size
        spirit_ball_y = self.board_coord[1] + new_row * self.cell_size
        self.spirit_ball_rect = self.spirit_ball.get_rect(topleft=(spirit_ball_x, spirit_ball_y))

    def load_skill_gold_(self):
        # get the number of self.skill and self.yellow_cell then display it to the screen
        self.skill_text = self.font.render(f'{self.skill}', True, self.WHITE)
        self.yellow_cell_text = self.font.render(f'{self.yellow_cells}', True, self.WHITE)
    
    def load_assets(self):
        self.assets_dir = os.path.join("assets")
        self.states_dir = os.path.join(self.assets_dir, "states")
        self.font_dir = os.path.join(self.assets_dir, "font")
        self.board_dir = os.path.join(self.assets_dir, "board")
        self.images_dir = os.path.join(self.board_dir, "img")
        self.gif_dir = os.path.join(self.board_dir, "gif")
        self.tile_status = os.path.join(self.images_dir, "tile_status")
        self.font = pygame.font.Font(os.path.join(self.font_dir, "PressStart2P-Regular.ttf"), 20)
        self.gif_obj = gif.load(os.path.join(self.states_dir, "board.gif"))


# remove it later
from game_state_manager import GameStateManager
if __name__=='__main__':
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    game_state_manager = GameStateManager('wumpus')
    wumpus = WumpusWorld(screen, game_state_manager, 'select_game_mode_2', 'select_world_size_4')
    states = {
        'wumpus': wumpus
    }
    states[game_state_manager.get_state()].run()