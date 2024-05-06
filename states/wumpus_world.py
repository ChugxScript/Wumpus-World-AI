import os
import pygame
import gif_pygame as gif
import random
import copy
from states.win import Win
from states.lose import Lose

class WumpusWorld():
    def __init__(self, display, gameStateManager):
        pygame.init()
        self.display = display
        self.gameStateManager = gameStateManager
        self.FPS = 60
        self.WHITE = (255, 255, 255)
        self.clock = pygame.time.Clock() 

        self.player_moves = {
            (0,0): "",
        }
            
        self.path = [[0,0]]

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
        self.is_remove_wall = False

        self.is_win_lose = False
        self.win = Win(self.display, self.gameStateManager)
        self.lose = Lose(self.display, self.gameStateManager)

    def run(self, current_player, current_world_size):
        self.current_player = current_player
        self.current_world_size = current_world_size
        self.load_assets()
        self.set_world_size() 
        self.create_world()
        self.set_player()  

        # put player_avatar on top of the starting cell
        self.update_player_avatar_position(0, 0)
        self.temp = self.check_valid_move(0, 0)
        self.cover_cells()
        self.load_skill_gold_()
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
                                self.is_remove_wall = not self.is_remove_wall
                                self.draw_cell()
                            if rect["id"] == 2:
                                self.reset_game()
                                self.set_world_size() 
                                self.create_world()
                                self.set_player() 
                                self.update_player_avatar_position(0, 0)
                                self.temp = self.check_valid_move(0, 0)
                                self.load_skill_gold_()
                            if rect["id"] == 3:
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

            if self.is_AI:
                self.ai()
                pygame.time.wait(60)
            
            self.display.fill((255, 255, 255))
            self.gif_obj.render(self.display, (0, 0)) # gif background
            self.display.blit(self.board_surface, self.board_coord) # board
            if not self.is_remove_wall:
                self.display.blit(self.cover_board_surface, self.board_coord)
                self.cover_cells()
            self.display.blit(self.player_avatar, self.player_avatar_rect) # player
            self.display.blit(self.cell_status, (725, 268)) # tile status
            self.display.blit(self.skill_text, (900, 115))
            self.display.blit(self.yellow_cell_text, (900, 180))

            self.draw_rectangles()
            pygame.display.flip()

            
                
            if self.is_win_lose:
                self.gameStateManager.get_state().run(self.player_score)
            self.clock.tick(self.FPS)
    
    def set_player(self):
        if self.current_player == 'select_game_mode_1':
            # set player to AI
            self.is_player = False
            self.is_AI = True
            self.ai_init()
            # self.ai()
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
            self.pit_cells_prob = 0.5 # 0.2 is too low
            self.wumpus_cells = 1
            self.gold_cells = 1
            self.skill = 1
        elif self.current_world_size == 'select_world_size_2':
            self.board_size = 6
            self.cell_size = 83
            self.board_coord = (78, 50)
            self.pit_cells_prob = 0.6
            self.wumpus_cells = 3
            self.gold_cells = 1
            self.skill = 2
        elif self.current_world_size == 'select_world_size_3':
            self.board_size = 8
            self.cell_size = 62
            self.board_coord = (82, 50)
            self.pit_cells_prob = 0.7
            self.wumpus_cells = 5
            self.gold_cells = 2
            self.skill = 3
        elif self.current_world_size == 'select_world_size_4':
            self.board_size = 10
            self.cell_size = 50
            self.board_coord = (82, 50)
            self.pit_cells_prob = 0.8
            self.wumpus_cells = 7
            self.gold_cells = 3
            self.skill = 5
        else:
            print(f"Invalid self.current_world_size: {self.current_world_size}")

    def create_world(self): # wow minecraft 
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        self.board_surface = pygame.Surface((self.board_width, self.board_height))

        self.world = [['' for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        for w in self.world:
            print(w)
        components = []

        # FLOW:
        # generate board base on the set world size
        # generate pit, wumpus, and gold cells according to the world size
        #   I take into the account to avoid generating pit or wumpus or gold next to the starting cell to make the game playable
        #   example scenario is 
        #       if in (0, 1) is pit and in (1, 0) is wumpus then the player is stuck; 
        #       if either one of those cells is gold then the game is finish already

        # to make sure that there is a path from start cell to gold cells I use dfs algorithm
        # is that needed?
        # example scenario is if all of the adjacent sides of gold cell are all pits 
        # then there is no way for the player to get the gold and win the game
        # therefor its needed (to have a path atleast)

        # NOTE: 
        # 'P' for pit cells
        # 'W' for wumpus cells
        # 'G' for gold cells
        # 'B' for breeze cells
        # 'S' for stench cells
        # 'V' for visited cells
        # (0, 0) is the start cell >:P

        gold_cells_placed = 0        
        while gold_cells_placed < self.gold_cells:
            while True:
                row = random.randint(0, self.board_size - 1)
                col = random.randint(0, self.board_size - 1)
                if self.world[row][col] == '' and abs(row - 0) + abs(col - 0) > 2 and not (row == 0 and col == 0):
                    self.world[row][col] = 'G'
                    components.append([[row, col], 'G'])
                    gold_cells_placed += 1
                    break

        wumpus_cells_placed = 0
        while wumpus_cells_placed < self.wumpus_cells:
            while True:
                row = random.randint(0, self.board_size - 1)
                col = random.randint(0, self.board_size - 1)
                is_valid_wumpus = False
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        w_row = row + dr
                        w_col = col + dc
                        if 0 <= w_row < self.board_size and 0 <= w_col < self.board_size:
                            if self.world[w_row][w_col] == 'G':
                                is_valid_wumpus = True
                                break
                    if is_valid_wumpus:
                        break
                
                if not is_valid_wumpus:
                    if self.world[row][col] == '' and not ((row == 0 and col == 1) or (row == 1 and col == 0) or (row == 0 and col == 0) or (row == 1 and col == 1)):
                        self.world[row][col] = 'W'
                        components.append(((row, col), 'W'))
                        wumpus_cells_placed += 1
                        break

        for _ in range(int(self.pit_cells_prob * self.board_size)):
            while True:
                row = random.randint(0, self.board_size - 1)
                col = random.randint(0, self.board_size - 1)
                is_valid_pit = False
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        w_row = row + dr
                        w_col = col + dc
                        if 0 <= w_row < self.board_size and 0 <= w_col < self.board_size:
                            if self.world[w_row][w_col] == 'G':
                                is_valid_pit = True
                                break
                    if is_valid_pit:
                        break
                if not is_valid_pit:
                    if self.world[row][col] == '' and not ((row == 0 and col == 1) or (row == 1 and col == 0) or (row == 0 and col == 0) or (row == 1 and col == 1)):
                        self.world[row][col] = 'P'
                        components.append(((row, col), 'P'))
                        break
        
        
        for pos, stat in components:
            if pos[0] + 1 < self.board_size:
                self.create_perceives(pos[0]+1, pos[1], stat)
            if pos[0] - 1 >= 0:
                self.create_perceives(pos[0]-1, pos[1], stat)

            # NOTE: isnt suppose to be pos[1] + 1 ??? since were checking the adjacent right cell ?
            if pos[1] + 1 < self.board_size:
                self.create_perceives(pos[0], pos[1]+1, stat)
            if pos[1] - 1 >= 0:
                self.create_perceives(pos[0], pos[1]-1, stat)
        
        # Check if there's a path from the starting cell to each gold cell
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.world[row][col] == 'G':
                    if not self.is_valid_path(0, 0, row, col):
                        self.create_world()  # Restart drawing board if path is not valid
                        return
        
        print(f"\n>>[1a]")
        for w in self.world:
            print(w)

        self.draw_cell()

    def is_valid_path(self, start_row, start_col, end_row, end_col):
        visited = [[False for _ in range(self.board_size)] for _ in range(self.board_size)]

        # A DFS function to check if there is a path from start to end
        def dfs(row, col):
            if  row < 0 or row >= self.board_size or col < 0 or col >= self.board_size or self.world[row][col] in ['P', 'W'] or visited[row][col]:
                return False
            visited[row][col] = True
            
            if row == end_row and col == end_col:
                return True
            if dfs(row + 1, col) or dfs(row - 1, col) or dfs(row, col + 1) or dfs(row, col - 1):
                return True
            return False

        return dfs(start_row, start_col)
    
    def create_perceives(self, row, col, stats):
        if stats == 'W':
            if self.world[row][col] == '':
                self.world[row][col] = 'S'
            elif self.world[row][col] != 'W':
                self.world[row][col] += ',S'
        elif stats == 'P':
            if self.world[row][col] == '':
                self.world[row][col] = 'B'
            elif self.world[row][col] != 'P':
                self.world[row][col] += ',B'
        elif stats == 'G':
            pass
        else:
            print(f"\n>> INVALID stats: {stats}")
    
    def draw_cell(self):
        self.perceive_world = copy.deepcopy(self.world)
        cell_status = {
            'P': "pit.png",
            'W': "wumpus.png",
            'G': "gold.png",
        }
        tile_status = {
            'start': "start_tile.png",
            '': "safe_tile.png",
            'S': "stench_tile.png",
            'SB': "stench_breeze_tile.png",
            'SG': "stench_glitter_tile.png",
            'B': "breeze_tile.png",
            'BG': "breeze_glitter_tile.png",
            'GL': "glitter_tile.png",
            'SBG': "stench_breeze_glitter_tile.png",
        }

        self.cell_images = {k: pygame.image.load(os.path.join(self.images_dir, v)) for k, v in cell_status.items()}
        for k, v in self.cell_images.items():
            self.cell_images[k] = pygame.transform.scale(v, (self.cell_size, self.cell_size))
        
        self.tile_images = {k: pygame.image.load(os.path.join(self.tile_status, v)) for k, v in tile_status.items()}
        for k, v in self.tile_images.items():
            self.tile_images[k] = pygame.transform.scale(v, (self.cell_size, self.cell_size))

        for row in range(self.board_size):
            for col in range(self.board_size):
                self.board_surface.blit(self.tile_images[''], (col * self.cell_size, row * self.cell_size))

                # Check if the cell is the starting position
                if row == 0 and col == 0:
                    self.board_surface.blit(self.tile_images['start'], (col * self.cell_size, row * self.cell_size))
                elif 'P' in self.world[row][col]:
                    self.board_surface.blit(self.cell_images['P'], (col * self.cell_size, row * self.cell_size))
                elif 'W' in self.world[row][col]:
                    self.board_surface.blit(self.cell_images['W'], (col * self.cell_size, row * self.cell_size))
                elif 'G' in self.world[row][col]:
                    self.board_surface.blit(self.cell_images['G'], (col * self.cell_size, row * self.cell_size))
                elif self.world[row][col] == 'B':
                    self.board_surface.blit(self.tile_images['B'], (col * self.cell_size, row * self.cell_size))
                else:
                    pit_adjacent = self.adjacent_cell(row + 1, col, 'P') or self.adjacent_cell(row - 1, col, 'P') or self.adjacent_cell(row, col + 1, 'P') or self.adjacent_cell(row, col - 1, 'P')
                    wumpus_adjacent = self.adjacent_cell(row + 1, col, 'W') or self.adjacent_cell(row - 1, col, 'W') or self.adjacent_cell(row, col + 1, 'W') or self.adjacent_cell(row, col - 1, 'W')
                    gold_adjacent = self.adjacent_cell(row + 1, col, 'G') or self.adjacent_cell(row - 1, col, 'G') or self.adjacent_cell(row, col + 1, 'G') or self.adjacent_cell(row, col - 1, 'G')

                    if pit_adjacent:
                        self.perceive_world[row][col] = 'B'
                        self.board_surface.blit(self.tile_images['B'], (col * self.cell_size, row * self.cell_size))

                    if wumpus_adjacent:
                        if self.perceive_world[row][col] != 'B':
                            self.perceive_world[row][col] = 'S'
                            self.board_surface.blit(self.tile_images['S'], (col * self.cell_size, row * self.cell_size))
                        else:
                            self.perceive_world[row][col] = 'S,B'
                            self.board_surface.blit(self.tile_images['SB'], (col * self.cell_size, row * self.cell_size))
                        

                    if gold_adjacent:
                        if self.perceive_world[row][col] != 'B' and self.perceive_world[row][col] != 'S':
                            self.perceive_world[row][col] = 'GL'
                            self.board_surface.blit(self.tile_images['GL'], (col * self.cell_size, row * self.cell_size))

                        elif self.perceive_world[row][col] == 'B':
                            self.perceive_world[row][col] = 'B,GL'
                            self.board_surface.blit(self.tile_images['BG'], (col * self.cell_size, row * self.cell_size))

                        elif self.perceive_world[row][col] == 'S':
                            self.perceive_world[row][col] = 'S,GL'
                            self.board_surface.blit(self.tile_images['SG'], (col * self.cell_size, row * self.cell_size))

                        elif self.perceive_world[row][col] == 'S,B':
                            self.perceive_world[row][col] = 'S,B,GL'
                            self.board_surface.blit(self.tile_images['SBG'], (col * self.cell_size, row * self.cell_size))
        
        # print(f"\n>>[1bb]")
        # for row in self.perceive_world:
        #     print(row)

        # create another board to serve as 'cover' to cover the unvisited cells

    def adjacent_cell(self, row, col, target):
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return False
        return target in self.world[row][col]  
        # return self.world[row][col] == target
    
    def cover_cells(self):
        self.cover_board_surface = pygame.Surface((self.board_width, self.board_height))
        self.cover_cell_img = pygame.image.load(os.path.join(self.images_dir, "unknown.png"))
        self.cover_cell_img = pygame.transform.scale(self.cover_cell_img, (self.cell_size, self.cell_size))
        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row, col) not in self.player_moves:
                    self.cover_board_surface.blit(self.cover_cell_img, (col * self.cell_size, row * self.cell_size))
                else:
                    self.cover_board_surface.blit(self.board_surface.subsurface((col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)), (col * self.cell_size, row * self.cell_size))

    def player_move_to(self, key):
        curr_row, curr_col = self.curr_position[0], self.curr_position[1]
        new_row, new_col = curr_row, curr_col  
        
        if self.is_player:
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
                if curr_row == 0 and curr_col == 0:
                    # start cell
                    if self.gold_cells == 0:
                        # climb out
                        self.player_score -= self.action_minus_score
                        self.gameStateManager.set_state(self.win)
                        self.is_win_lose = True
                        self.still_gold = False
                    else:
                        self.still_gold = True

                elif self.world[curr_row][curr_col] == 'G':
                    # grab the gold
                    self.world[curr_row][curr_col] = ''
                    self.draw_cell()
                    self.gold_cells -= 1
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
                            if 'W' in self.world[s_ball_row][s_ball_col]:
                                self.wumpus_hit = True
                                break
                            
                    if self.facing_in['below']:
                        while s_ball_row != self.board_size - 1:
                            s_ball_row += 1
                            self.fire_spirit_ball(s_ball_row, s_ball_col)
                            self.display.blit(self.spirit_ball, self.spirit_ball_rect)
                            pygame.display.flip()
                            pygame.time.wait(50)
                            if 'W' in self.world[s_ball_row][s_ball_col]:
                                self.wumpus_hit = True
                                break
                            
                    if self.facing_in['left']:
                        while s_ball_col != 0:
                            s_ball_col -= 1
                            self.fire_spirit_ball(s_ball_row, s_ball_col)
                            self.display.blit(self.spirit_ball, self.spirit_ball_rect)
                            pygame.display.flip()
                            pygame.time.wait(50)
                            if 'W' in self.world[s_ball_row][s_ball_col]:
                                self.wumpus_hit = True
                                break
                            
                    if self.facing_in['right']:
                        while s_ball_col != self.board_size - 1:
                            s_ball_col += 1
                            self.fire_spirit_ball(s_ball_row, s_ball_col)
                            self.display.blit(self.spirit_ball, self.spirit_ball_rect)
                            pygame.display.flip()
                            pygame.time.wait(50)
                            if 'W' in self.world[s_ball_row][s_ball_col]:
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

                        # if still crashing lower the value of self.display_time or pygame.time.wait

                        self.world[s_ball_row][s_ball_col] = ""
                        components = []
                        for nrow in range(self.board_size - 1):
                            for ncol in range(self.board_size - 1):
                                if 'G' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'G'))
                                if 'W' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'W'))
                                if 'P' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'P'))
                                if all(item not in self.world[nrow][ncol] for item in ['G', 'W', 'P']):
                                    self.world[nrow][ncol] = ''
                        
                        for pos, stat in components:
                            if pos[0] + 1 < self.board_size:
                                self.create_perceives(pos[0]+1, pos[1], stat)
                            if pos[0] - 1 >= 0:
                                self.create_perceives(pos[0]-1, pos[1], stat)

                            if pos[1] + 1 < self.board_size:
                                self.create_perceives(pos[0], pos[1]+1, stat)
                            if pos[1] - 1 >= 0:
                                self.create_perceives(pos[0], pos[1]-1, stat)
                        self.draw_cell()

                    self.load_skill_gold_()
        
        if self.is_AI:
            new_row, new_col = key
            if self.gold_cells == 0 and new_row == 0 and new_col == 0:
                self.player_score -= self.action_minus_score
                self.is_win_lose = True
                
        # Check if the new position is valid
        if self.check_valid_move(new_row, new_col):
            self.curr_position[0] = new_row
            self.curr_position[1] = new_col
            
            # store the cell and its status
            # if (new_row, new_col) in [tuple(cell) for cell in self.world]:
            self.player_moves[(new_row, new_col)] = self.perceive_world[new_row][new_col]

            print(f"\n>> self.player_moves: {self.player_moves}")
            self.update_player_avatar_position(new_row, new_col)

            # check if the current cell is a pit or a wumpus
            if 'P' in self.world[new_row][new_col]:
                self.action_minus_score += 1000
                self.player_score -= self.action_minus_score
                self.gameStateManager.set_state(self.lose)
                self.is_win_lose = True

            if 'W' in self.world[new_row][new_col]:
                self.action_minus_score += 1000
                self.player_score -= self.action_minus_score
                self.gameStateManager.set_state(self.lose)
                self.is_win_lose = True

    def check_valid_move(self, row, col):
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "bump_tile.png"))
            self.cell_status = pygame.transform.scale(self.cell_status, (200, 200))
            return False
        
        # check what value of y and x in self.cells
        self.curr_cell_value = self.perceive_world[row][col]
        print(f"\n>> self.curr_cell_value: {self.curr_cell_value}")
        
        if self.curr_cell_value == None:
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "safe_tile.png"))
        elif row == 0 and col == 0:
            if self.still_gold:
                # self.cell_status = pygame.image.load(os.path.join(self.tile_status, "still_golds_1.png")) # this one is formal
                self.cell_status = pygame.image.load(os.path.join(self.tile_status, "still_golds_2.png"))
                self.still_gold = False
            else: self.cell_status = pygame.image.load(os.path.join(self.tile_status, "start_tile.png"))
        elif self.curr_cell_value == 'P':
            self.cell_status = pygame.image.load(os.path.join(self.images_dir, "pit.png"))
        elif self.curr_cell_value == 'W':
            self.cell_status = pygame.image.load(os.path.join(self.images_dir, "wumpus.png"))
        elif self.curr_cell_value == 'G':
            self.cell_status = pygame.image.load(os.path.join(self.images_dir, "gold.png"))
        elif self.curr_cell_value == 'B':
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "breeze_tile.png"))
        elif self.curr_cell_value == 'S':
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "stench_tile.png"))
        elif self.curr_cell_value == 'GL':
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "glitter_tile.png"))
        elif self.curr_cell_value == 'S,B':
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "stench_breeze_tile.png"))
        elif self.curr_cell_value == 'B,GL':
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "breeze_glitter_tile.png"))
        elif self.curr_cell_value == 'S,GL':
            self.cell_status = pygame.image.load(os.path.join(self.tile_status, "stench_glitter_tile.png"))
        elif self.curr_cell_value == 'S,B,GL':
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
        self.yellow_cell_text = self.font.render(f'{self.gold_cells}', True, self.WHITE)

    def ai_init(self):
        # Constants
        self.S = 0
        self.B = 1
        self.P = 2
        self.W = 3
        self.V = 4
        self.G = 5
        self.c = 0
        self.r = 0
        self.path_to_gold = [[0,0]]
        self.kb = [[['' for _ in range(6)] for _ in range(self.board_size)] for _ in range(self.board_size)]

    def ai(self):
        if self.gold_cells != 0:
            print(f"\n>> AI is on: ({self.r}, {self.c})")
            self.learn_from_pos()
            # self.path_to_gold.append([self.r, self.c])
            self.next_xy = []
            self.print_kb()
            
            if 'G' in self.perceives():
                self.gold_cells -= 1
                self.player_score += 1000
                self.load_skill_gold_()
                self.update_perceive('gold', (0,0))
                self.draw_cell()
                if self.gold_cells == 0:
                    self.still_gold = False
                    self.gameStateManager.set_state(self.win)
                else: self.still_gold = True
                print(f"\n>> GOT THE GOLD ----")
            
            for (x, y), _ in self.adjacent():
                if "~W" == self.kb[x][y][self.W]:
                    if "~P" == self.kb[x][y][self.P]:
                        if "V" != self.kb[x][y][self.V]:
                            self.next_xy = [x, y]
                            break
            
            print(f">> 1self.path_to_gold: {self.path_to_gold}")
            print(f">> self.path: {self.path}")
            print(f">> self.path_to_gold: {self.path_to_gold}")
            print(f">> self.next_xy: {self.next_xy}")

            if len(self.next_xy) > 0:
                self.path.append([self.next_xy[0],self.next_xy[1]])
                self.path_to_gold.append([self.next_xy[0],self.next_xy[1]])
                # self.move(self.next_xy[0], self.next_xy[1])
            else:
                if len(self.path_to_gold) > 1:
                    self.next_xy = self.path_to_gold.pop()
                    self.path.append([self.next_xy[0],self.next_xy[1]])
                    
                    # self.move(self.next_xy[0], self.next_xy[1])
                else:
                    # reset all visited cells
                    for i in range(len(self.kb)):
                        for j in range(len(self.kb[i])):
                            if i == 0 and j == 0:
                                continue
                            else:
                                self.kb[i][j][self.V] = ""
                    self.next_xy = [0, 0]
            
            self.r, self.c = self.next_xy[0], self.next_xy[1]
            self.action_minus_score += 1
            self.player_move_to(self.next_xy)
            print(f"\n>> self.kb[{self.r}][{self.c}]: {self.kb[self.r][self.c]}")
            # input(print("\n>>>>>>>>>>>>>>"))
        
        else:
            self.player_move_to(self.path.pop())

    def learn_from_pos(self):
        actual_components = self.perceives()
        print(f">> actual_components: {actual_components}")
        self.next_xy = []

        self.kb[self.r][self.c][self.S] = ("S" if "S" in actual_components else "~S")
        self.kb[self.r][self.c][self.B] = ("B" if "B" in actual_components else "~B")
        self.kb[self.r][self.c][self.P] = ("P" if "P" in actual_components else "~P")
        self.kb[self.r][self.c][self.W] = ("W" if "W" in actual_components else "~W")
        self.kb[self.r][self.c][self.V] = "V"
        self.kb[self.r][self.c][self.G] = ("G" if "G" in actual_components else "~G")       

        for (nrow, ncol), stats in self.adjacent():
            if "S" in actual_components:
                if "W?" in self.kb[nrow][ncol][self.W]:
                    if "V" not in self.kb[nrow][ncol]:
                        self.kb[nrow][ncol][self.W] = "W"
                        if self.skill != 0:
                            print(f"\n>> wumpus killed in self.kb[{nrow}][{ncol}]")
                            print(f">> self.skill: {self.skill}")
                            self.skill -= 1
                            self.load_skill_gold_()
                            self.update_perceive('enemy', (nrow, ncol))
                elif "~W" not in self.kb[nrow][ncol][self.W]:
                    self.kb[nrow][ncol][self.W] = "W?"
            else:
                self.kb[nrow][ncol][self.W] = "~W"

            if "B" in actual_components:
                if "P?" in self.kb[nrow][ncol][self.P]:
                    if "V" not in self.kb[nrow][ncol]:
                        self.kb[nrow][ncol][self.P] = "P"
                elif "~P" not in self.kb[nrow][ncol][self.P]:
                    self.kb[nrow][ncol][self.P] = "P?"
            else:
                self.kb[nrow][ncol][self.P] = "~P"
            
    
    def perceives(self):
        return self.world[self.r][self.c]
    
    def adjacent(self):
        rows = self.board_size
        cols = self.board_size
        locations = []
        for row in [self.r - 1, self.r + 1]:
            if 0 <= row < rows:
                locations.append(((row, self.c), self.world[row][self.c]))
        for col in [self.c - 1, self.c + 1]:
            if 0 <= col < cols:
                locations.append(((self.r, col), self.world[self.r][col]))
        return locations

    def print_kb(self):
        print("\n>>>>>>>>>>>>>>>>>> WORLD")
        for r in range(self.board_size):
            for c in range(self.board_size):
                print('{:>2}'.format(self.world[r][c]), end=' | ')
            print()
        
        print("\n>>>>>>>>>>>>>>>>>> AGENT")
        for r in range(self.board_size):
            for c in range(self.board_size):
                for x in range(6):
                    print('{:>2},'.format(self.kb[r][c][x]), end='')
                print(' | ', end='')
            print('\n')
    
    def update_perceive(self, mode, rowCol):
        if mode == 'gold':
            self.world[self.r][self.c] = ""
            for _, stat in self.adjacent():
                if "P" in stat:
                    if self.world[self.r][self.c] == "":
                        self.world[self.r][self.c] = "B"
                    else:
                        self.world[self.r][self.c] += ",B"
                    self.kb[self.r][self.c][self.B] = "B"
                else:
                    self.kb[self.r][self.c][self.B] = "~B"

                if "W" in stat:
                    if self.world[self.r][self.c] == "":
                        self.world[self.r][self.c] = "S"
                    else:
                        self.world[self.r][self.c] += ",S"
                    self.kb[self.r][self.c][self.S] = "S"
                else:
                    self.kb[self.r][self.c][self.S] = "~S"
        
        elif mode == 'enemy':
            row, col = rowCol
            s_ball = self.board_size -1
            if row != self.r:
                while s_ball != 0:
                    s_ball -= 1
                    if 'W' in self.world[s_ball][col]:
                        self.world[s_ball][col] = ""
                        self.kb[s_ball][col][self.W] = "~W"
                        self.kb[self.r][self.c][self.S] = "~S"
                        components = []
                        for nrow in range(self.board_size - 1):
                            for ncol in range(self.board_size - 1):
                                if 'G' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'G'))
                                if 'W' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'W'))
                                if 'P' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'P'))
                                if all(item not in self.world[nrow][ncol] for item in ['G', 'W', 'P']):
                                    self.world[nrow][ncol] = ''
                        
                        for pos, stat in components:
                            if pos[0] + 1 < self.board_size:
                                self.create_perceives(pos[0]+1, pos[1], stat)
                            if pos[0] - 1 >= 0:
                                self.create_perceives(pos[0]-1, pos[1], stat)

                            if pos[1] + 1 < self.board_size:
                                self.create_perceives(pos[0], pos[1]+1, stat)
                            if pos[1] - 1 >= 0:
                                self.create_perceives(pos[0], pos[1]-1, stat)
                        self.draw_cell()

            elif col != self.c:
                while s_ball != 0:
                    s_ball -= 1
                    if 'W' in self.world[row][s_ball]:
                        self.world[row][s_ball] = ""
                        self.kb[row][s_ball][self.W] = "~W"
                        self.kb[self.r][self.c][self.S] = "~S"
                        components = []
                        for nrow in range(self.board_size - 1):
                            for ncol in range(self.board_size - 1):
                                if 'G' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'G'))
                                if 'W' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'W'))
                                if 'P' in self.world[nrow][ncol]:
                                    components.append(((nrow, ncol), 'P'))
                                if all(item not in self.world[nrow][ncol] for item in ['G', 'W', 'P']):
                                    self.world[nrow][ncol] = ''
                        
                        for pos, stat in components:
                            if pos[0] + 1 < self.board_size:
                                self.create_perceives(pos[0]+1, pos[1], stat)
                            if pos[0] - 1 >= 0:
                                self.create_perceives(pos[0]-1, pos[1], stat)

                            if pos[1] + 1 < self.board_size:
                                self.create_perceives(pos[0], pos[1]+1, stat)
                            if pos[1] - 1 >= 0:
                                self.create_perceives(pos[0], pos[1]-1, stat)
                        self.draw_cell()

    def draw_rectangles(self):
        WHITE = (255,255 , 255)
        self.rectangles = [
            {"id": 1, "rect": pygame.Rect(687, 470, 80, 80)},
            {"id": 2, "rect": pygame.Rect(767, 470, 85, 80)},
            {"id": 3, "rect": pygame.Rect(852, 470, 115, 80)}
        ]
        for rect in self.rectangles:
            pygame.draw.rect(self.display, WHITE, rect["rect"], 1)
    
    def reset_game(self):
        # Reset game parameters to initial state
        self.player_moves = {(0,0): ""}
        self.path = [[0,0]]
        self.facing_in = {'right': True, 'left': False, 'above': False, 'below': False}
        self.curr_position = [0, 0]
        self.player_score = 0
        self.action_minus_score = 0
        self.still_gold = False
        self.is_win_lose = False
    
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
