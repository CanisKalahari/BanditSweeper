import enum
import random as rnd

import numpy as np

class GameStatus(enum.Enum):
    ONGOING = 0
    WIN = 1
    LOSS = 2

class TileStatus(enum.Enum):
    COVERED = None
    UNCOVERED = 1
    FLAGGED = 10

MINE_NUM = 9

class Game:
    def __init__(self, n_rows, n_cols, n_mines, b_sub = None):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.n_mines = n_mines
        self.n_uncovered = self.n_flagged = 0
        self.status = GameStatus.ONGOING
        
        self.tile_status = np.full((self.n_rows, self.n_cols), TileStatus.COVERED)
        self.tile_num = np.zeros((self.n_rows, self.n_cols), int)
        
        if b_sub is None:
            coords_gen = np.ndindex(self.tile_num.shape)
            bombs = rnd.sample(list(coords_gen), self.n_mines)
        else:
            bombs = b_sub
            
        for x, y in bombs:
            self.tile_num[x][y] = MINE_NUM
                            
            for u in [-1, 0, 1]:
                for v in [-1, 0, 1]:
                    if u == v == 0:
                        continue
                    xu = x + u
                    yv = y + v
                    if self.is_inside_board(xu, yv):
                        if not self.is_mine(xu, yv):
                            self.tile_num[xu][yv] += 1

    def is_inside_board(self, x, y):
        return 0 <= x < self.n_rows and 0 <= y < self.n_cols
                        
    def get_board(self):
        covered = self.tile_status == TileStatus.COVERED
        flagged = self.tile_status == TileStatus.FLAGGED

        board = np.where(covered, TileStatus.COVERED.value, self.tile_num)
        board = np.where(flagged, TileStatus.FLAGGED.value, board)
        return board.tolist()
    
    def get_bomb_map(self):
        return self.tile_num == MINE_NUM
    
    def is_over(self):
        return self.status != GameStatus.ONGOING

    def is_mine(self, x, y):
        return self.tile_num[x][y] == MINE_NUM
    
    def click(self, x, y):
        if self.tile_status[x][y] != TileStatus.COVERED:
            raise Exception('There is something wrong')
        
        if self.is_mine(x, y):
            self.tile_status[x][y] = TileStatus.UNCOVERED
            self.status = GameStatus.LOSS
            return True
        
        self._uncover_tiles(x, y)
        
        return False
    
    def _uncover_tiles(self, x, y):
        stack = [(x, y)]
        
        while stack:
            x, y = stack.pop()
            
            if self.tile_status[x][y] != TileStatus.COVERED:
                continue
            
            self.tile_status[x][y] = TileStatus.UNCOVERED
            self.n_uncovered += 1
            
            if self.tile_num[x][y] == 0: # If the tile is blank uncover surrounding tiles
                for u in [-1, 0, 1]:
                    for v in [-1, 0, 1]:
                        xu = x + u
                        yv = y + v
                        if self.is_inside_board(xu, yv):
                            if self.tile_status[xu][yv] == TileStatus.COVERED:
                                stack.append((xu, yv))

        if self.n_uncovered == self.n_rows * self.n_cols - self.n_mines:
            self.status = GameStatus.WIN
                            
    def set_flag(self, x, y):
        if self.tile_status[x][y] == TileStatus.COVERED:
            self.tile_status[x][y] = TileStatus.FLAGGED
            self.n_flagged += 1
        
        return self.n_flagged > self.n_mines
    
    def remove_flag(self, x, y):
        if self.tile_status[x][y] == TileStatus.FLAGGED:
            self.tile_status[x][y] = TileStatus.COVERED
            self.n_flagged -= 1
