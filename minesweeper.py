import random
import pdb
import numpy as np
from scipy import signal
from scipy import ndimage
from pprint import pprint

WINREWARD = 1
LOSREWARD = -10
PROGRESSREWARD = 1


w_k = np.array(    [[1, 1, 1],
                    [1, 0, 1],
                    [1, 1, 1],],
                   dtype='int')

class GameConfig(object):
    def __init__(self, width=8, height=8, num_mines=10, winr=0, progr=0, lossr=1, flag_hitr=1, flag_missr=0):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.winr = winr
        self.progr = progr
        self.lossr = lossr
        self.flag_hitr = flag_hitr
        self.flag_missr = flag_missr
        self.cellsStateCount=10

class Game(object):
    def __init__(self, config):
        self.width = config.width
        self.height = config.height
        self.winr = config.winr
        self.progr = config.progr
        self.lossr = config.lossr
        self.num_mines = config.num_mines
        self.board = [[False for y in range(self.height)] for x in range(self.width)]
        self.exposed = [[False for y in range(self.height)] for x in range(self.width)]
        self.counts = [[0 for y in range(self.height)] for x in range(self.width)]
        self.num_moves = 0
        self.num_safe_squares = self.width * self.height - self.num_mines
        self.num_exposed_squares = 0
        self.explosion = False
        self.flags = set()

        self._place_mines()
        self._init_counts()
        
    def set_flag(self, x, y):
        self.flags.add((x, y))
        
        return len(self.flags) > self.num_mines
        
    def unset_flag(self, x, y):
        #pprint(self.flags)
        self.flags.remove((x, y))

    def select(self, x, y):
        """
        Select a square to expose. Coordinates are zero based.
        If the square has already been selected, returns None.
        Returns a MoveResult object with success/failure and a 
        list of squares exposed.
        """
        if (x, y) in self.flags:
            print('You cant select a tile with a flag')
            return None
        if self._is_outside_board(x, y):
            # raise ValueError('Position ({0},{1}) is outside the board'.format(x, y))
            print("_________________________________ WRONG 1 ~> ", str(x), str(y))
            pprint(self.get_state())
            pprint(self.board)
            return None
        if self.explosion:
            print("_________________________________ WRONG 2 ~> ", str(x), str(y))
            pprint(self.get_state())
            pprint(self.board)
            return None
        if self.exposed[x][y]:
            print("_________________________________ WRONG ~> ", str(x), str(y))
            pprint(self.get_state())
            pprint(self.board)
            return None
        self.num_moves += 1
        if self.board[x][y]:
            self.explosion = True
            self.exposed[x][y] = True
            return MoveResult(True, False, reward=self.lossr)

        updatedBoard=self._update_board(x, y)
        if self.num_exposed_squares == self.num_safe_squares:
            # pdb.set_trace()
            return MoveResult(False, True, updatedBoard ,reward=self.winr)
        return MoveResult(False, False, updatedBoard,reward=self.progr)

    def get_state(self):
        """
        Get the current state of the game
        None means not exposed and the rest are counts
        This does not contain the exploded mine if one exploded.
        """

        # state = [[None for y in range(self.height)] for x in range(self.width)]
        # for x in range(self.width):
        #     for y in range(self.height):
        #         if self.exposed[x][y]:
        #             state[x][y] = self.counts[x][y]
        # pdb.set_trace()

        state = np.asarray([[None]*self.height]*self.width)
        counts = np.asarray(self.counts)
        exposed = np.asarray(self.exposed)
        state[exposed] = counts[exposed]
        
        for flag in self.flags:
            state[flag[0]][flag[1]] = 10 # 10 indicates a flag
        
        return state.tolist()

    def is_game_over(self):
        return self.explosion or self.num_exposed_squares == self.num_safe_squares

    def set_flags(self, flags):
        self.flags = flags
        
    def get_conf(self, i, j, game_state):
        conf = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        len_col = len(game_state)
        len_row = len(game_state[0])
        
        if i == 0 or j == 0:
            conf[0] += 1
        else:
            aux = game_state[i-1][j-1] if game_state[i-1][j-1] != None else 0
            conf[aux] += 1
            
        if i == 0 or j == len_row -1:
            conf[0] += 1
        else:
            aux = game_state[i-1][j+1] if game_state[i-1][j+1] != None else 0
            conf[aux] += 1
            
        if i == len_col - 1 or j == len_row - 1:
            conf[0] += 1
        else:
            aux = game_state[i+1][j+1] if game_state[i+1][j+1] != None else 0
            conf[aux] += 1
            
        if i == len_col - 1 or j == 0:
            conf[0] += 1
        else:
            aux = game_state[i+1][j-1] if game_state[i+1][j-1] != None else 0
            conf[aux] += 1
            
        if i == 0:
            conf[0] += 1
        else:
            aux = game_state[i-1][j] if game_state[i-1][j] != None else 0
            conf[aux] += 1
            
        if j == 0:
            conf[0] += 1
        else:
            aux = game_state[i][j-1] if game_state[i][j-1] != None else 0
            conf[aux] += 1
            
        if i == len_col - 1:
            conf[0] += 1
        else:
            aux = game_state[i+1][j] if game_state[i+1][j] != None else 0
            conf[aux] += 1
            
        if j == len_row - 1:
            conf[0] += 1
        else:
            aux = game_state[i][j+1] if game_state[i][j+1] != None else 0
            conf[aux] += 1
            
        return conf

    def _place_mines(self):
        mines = set()
        while len(mines) < self.num_mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            mines.add((x, y))
            self.board[x][y] = True
        # for coords in mines:
        #     self.board[coords[0]][coords[1]] = True

    def _init_counts(self):
        """Calculates how many neighboring squares have minds for all squares"""
        # pdb.set_trace()
        
        # for x in range(self.width):
        #     for y in range(self.height):
        #         for x_offset in [-1, 0, 1]:
        #             for y_offset in [-1, 0, 1]:
        #                 if x_offset != 0 or y_offset != 0:
        #                     if not self._is_outside_board(x + x_offset, y + y_offset):
        #                         self.counts[x][y] += int(self.board[x + x_offset][y + y_offset])
        x = np.asarray(self.board,'int')
        # self.counts = (signal.convolve2d(x, w_k, 'same')).tolist()
        self.counts = np.asarray(self.counts,'int')
        ndimage.convolve(x,w_k, output=self.counts ,mode='constant')
        self.counts = self.counts.tolist()

    def _update_board(self, x, y):
        """
        Finds all the squares to expose based on a selection
        This uses an 8 neighbor region growing algorithm to expand the board if
        the chosen square is not a neighbor to a mine.
        """
        self._expose_square(x, y)
        squares = [Position(x, y, self.counts[x][y])]
        if self.counts[x][y] != 0:
            return squares

        stack = [(x, y)]
        while len(stack) > 0:
            (x, y) = stack.pop()
            for x_offset in [-1, 0, 1]:
                for y_offset in [-1, 0, 1]:
                    if x_offset != 0 or y_offset != 0:
                        new_x = x + x_offset
                        new_y = y + y_offset
                        if not self._is_outside_board(new_x, new_y):
                            #if not self.exposed[new_x][new_y]:
                            if not self.exposed[new_x][new_y] and (new_x, new_y) not in self.flags:
                                self._expose_square(new_x, new_y)
                                squares.append(Position(new_x, new_y, self.counts[new_x][new_y]))
                                if self._test_count(new_x, new_y):
                                    stack.append((new_x, new_y))
        return squares

    def _expose_square(self, x, y):
        self.exposed[x][y] = True
        self.num_exposed_squares += 1

    def _test_count(self, x, y):
        """Does this square have a count of zero?"""
        return self.counts[x][y] == 0

    def _is_outside_board(self, x, y):
        if x < 0 or x == self.width:
            return True
        if y < 0 or y == self.height:
            return True
        return False

    def IsActionValid(self,row,col):
        return not(self.exposed[row][col])

class Position(object):
    def __init__(self, x, y, num_neighbors):
        self.x = x
        self.y = y
        self.num_bomb_neighbors = num_neighbors

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.num_bomb_neighbors == other.num_bomb_neighbors


class MoveResult(object):
    def __init__(self, explosion, win, new_squares=[],reward=0):
        self.explosion = explosion
        self.win = win
        self.new_squares = new_squares
        self.reward = reward

    def __eq__(self, other):
        if self.explosion != other.explosion:
            return False
        return set(self.new_squares) == set(other.new_squares)


class GameResult(object):
    def __init__(self, success, num_moves):
        self.success = success
        self.num_moves = num_moves