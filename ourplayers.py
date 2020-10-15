import random
import collections as cl
import numpy as np
import confms
from pprint import pprint
import oursweeper

class DummyPlayer:
    def __init__(self, args):
        print('Dummy Player args:', args)
        
    def call_play(self, game_state):
        pass
    
    def pick_flag(self, game_state):
        pass
      
    def mind_play(self, play_result):
        pass
    
    def mind_game(self, bomb_map):
        pass
    

class ActionData:
    def __init__(self, Q=0, count=0):
        self.Q = Q
        self.count = count

    def __repr__(self):
        return f'ActionData(Q={self.Q}, count={self.count})'


class MegreedyPlayer:
    def __init__(self, E=0.0, F=0.1, safe_reward=-1, bomb_reward=1, unseen_q=1-1e-5):
        self.E = E
        self.F = F
        self.safe_reward = safe_reward
        self.bomb_reward = bomb_reward
        self.unseen_q = unseen_q
        self.np_actions = 0

        self.actions = cl.defaultdict(ActionData)

        self.last_call = None
        self.last_game_state = None
        self.flag_plays = []
        
    #@profile
    def call_play(self, game_state):
        len_row = len(game_state)
        len_col = len(game_state[0])

        to_explore = np.random.choice([True, False], p=[self.E, 1.-self.E])
        
        the_q = 0
        the_count = 0

        pos = []

        for i in range(len_row):
            for j in range(len_col):

                if game_state[i][j] is not oursweeper.TileStatus.COVERED.value:
                    continue

                conf_index = 9

                for u in [-1, 0, 1]:
                    for v in [-1, 0, 1]:
                        conf_index -= 1

                        if u == v == 0 or not (0 <= i + u < len_row and 0 <= j + v < len_col):
                            continue

                        config = confms.get_conf_ult(i+u, j+v, conf_index, game_state, self.actions)
                        
                        if to_explore:
                            pos.append((config, (i, j)))
                            continue
                            
                        q_val = self.actions[config].Q if config in self.actions else self.unseen_q
                        count_val = self.actions[config].count if config in self.actions else 0
                        
                        if abs(q_val) > abs(the_q) or (abs(q_val) == abs(the_q) and count_val > the_count):
                            coord = (i, j)
                            the_q = q_val
                            the_count = count_val
                            the_action = config
                            

        if to_explore:
            
            the_action, coord = pos[random.randint(0, len(pos)-1)]

            #the_q = np.random.choice([-1, 1], p=[1.-self.F, self.F])
            the_q = self.actions[the_action].Q if the_action in self.actions else self.unseen_q

        play = {}
        play['x'] = coord[0]
        play['y'] = coord[1]
        play['q'] = the_q
        
#         if the_action not in self.actions:
#             self.np_actions += 1
        
        if the_q < 0.:
            play['type'] = 'safe'
        else:
            play['type'] = 'flag'
            self.flag_plays.append((the_action, play['x'], play['y']))
        
        self.last_call = the_action
        self.last_game_state = game_state

        return play
    
    def pick_flag(self, game_state):
        len_row = len(game_state)
        len_col = len(game_state[0])
        
        the_q = float('inf')

        for i in range(len_row):
            for j in range(len_col):

                if game_state[i][j] != oursweeper.TileStatus.FLAGGED.value:
                    continue
                    
                game_state[i][j] = oursweeper.TileStatus.COVERED.value

                conf_index = 9

                for u in [-1, 0, 1]:
                    for v in [-1, 0, 1]:
                        conf_index -= 1

                        if u == v == 0 or not (0 <= i + u < len_row and 0 <= j + v < len_col):
                            continue

                        config = confms.get_conf_ult(i+u, j+v, conf_index, game_state, self.actions)
                            
                        q_val = self.actions[config].Q if config in self.actions else self.unseen_q

                        if q_val <= the_q:
                            coord = (i, j)
                            the_q = q_val
                            the_action = config

                game_state[i][j] = oursweeper.TileStatus.FLAGGED.value
        
        play = {}
        play['x'] = coord[0]
        play['y'] = coord[1]
        play['q'] = the_q
        play['type'] = 'safe'
        
#         if the_action not in self.actions:
#             self.np_actions += 1
        
        self.last_call = the_action

        return play
      
    def mind_play(self, play_result): # Lida com os resultados de uma jogada
        conf = self.last_call
        
        reward = self.bomb_reward if play_result else self.safe_reward
        
        if conf not in self.actions:
            self.np_actions += 1
        
        past_q = self.actions[conf].Q

        self.actions[conf].count += 1
        self.actions[conf].Q += (1./self.actions[conf].count)*(reward - past_q)
        
        new_q = self.actions[conf].Q
        
        if abs(past_q) == 1 and abs(new_q) != 1:
            self.np_actions -= 1

        self.last_call = None
    
    #@profile
    def mind_game(self, bomb_map): # Lida com as flags pós-jogo
        nwf = 0 # number of wrong flags
        
        for conf, x, y in self.flag_plays:
            reward = self.bomb_reward if bomb_map[x][y] else self.safe_reward
            
            nwf += 0 if bomb_map[x][y] else 1
            
            past_q = self.actions[conf].Q

            self.actions[conf].count += 1
            self.actions[conf].Q += (1./self.actions[conf].count)*(reward - self.actions[conf].Q)
            
            new_q = self.actions[conf].Q
            
            if abs(past_q) == 1 and abs(new_q) != 1:
                self.np_actions -= 1
            
        game_state = self.last_game_state
            
        len_row = len(game_state)
        len_col = len(game_state[0])

        for i in range(len_row):
            for j in range(len_col):

                if game_state[i][j] is not oursweeper.TileStatus.COVERED.value:
                    continue

                conf_index = 9

                for u in [-1, 0, 1]:
                    for v in [-1, 0, 1]:
                        conf_index -= 1

                        if u == v == 0 or not (0 <= i + u < len_row and 0 <= j + v < len_col):
                            continue
                            
                        #if game_state[i+u][j+v] == 10 and not bomb_map[i+u][j+v]:
                        #    continue

                        conf = confms.get_conf_ult(i+u, j+v, conf_index, game_state, self.actions)
                        
                        #print(i + conf_index//3, j + conf_index%3)
                            
                        reward = self.bomb_reward if bomb_map[i][j] else self.safe_reward
                        
                        if conf not in self.actions:
                            self.np_actions += 1
                            
                        past_q = self.actions[conf].Q

                        self.actions[conf].count += 1
                        self.actions[conf].Q += (1./self.actions[conf].count)*(reward - self.actions[conf].Q)
                        
                        new_q = self.actions[conf].Q
                        
                        if abs(past_q) == 1 and abs(new_q) != 1:
                            self.np_actions -= 1
            
        self.flag_plays = []
        self.last_call = None
        self.last_game_state = None
        
        return nwf

class MUCBPlayer:
    def __init__(self, c=.1, safe_reward=-1, bomb_reward=1, unseen_type=0):
        self.c = c
        self.safe_reward = safe_reward
        self.bomb_reward = bomb_reward
        self.unseen_type = unseen_type

        self.t = 0
        self.max_count = 1

        self.actions = cl.defaultdict(ActionData)
        self.np_actions = 0

        self.last_call = None
        self.last_game_state = None
        self.flag_plays = []
        
    def call_play(self, game_state):
        len_row = len(game_state)
        len_col = len(game_state[0])
        
        self.t += 1
        
        the_q = 0
        
        for i in range(len_row):
            for j in range(len_col):

                if game_state[i][j] is not oursweeper.TileStatus.COVERED.value:
                    continue

                conf_index = 9

                for u in [-1, 0, 1]:
                    for v in [-1, 0, 1]:
                        conf_index -= 1
                        
                        if u == v == 0 or not (0 <= i + u < len_row and 0 <= j + v < len_col):
                            continue

                        config = confms.get_conf_ult(i+u, j+v, conf_index, game_state, self.actions)
                        
                        if config in self.actions:
                            q_val = self.actions[config].Q
                            ucb = self.c * np.sqrt(np.log(self.t) / self.actions[config].count)
                            q_val += np.sign(q_val) * ucb
                                
                        else:
                            q_val = -(1e10)
                            #q_val = self.safe_reward - self.c * np.sqrt(np.log(self.t))
#                             if self.unseen_type == 0:
#                                 q_val = self.safe_reward
#                             else:
#                                 q_val = self.safe_reward - self.c * np.sqrt(np.log(self.t)/self.max_count)

                        if abs(q_val) >= abs(the_q):
                            coord = (i, j)
                            the_q = q_val
                            the_action = config

        play = {}
        play['x'] = coord[0]
        play['y'] = coord[1]
        play['q'] = the_q
        
#         if the_action not in self.actions:
#             self.np_actions += 1
        
        if the_q < 0.:
            play['type'] = 'safe'
        else:
            play['type'] = 'flag'
            self.flag_plays.append((the_action, play['x'], play['y']))
        
        self.last_call = the_action
        self.last_game_state = game_state

        return play
    
    def pick_flag(self, game_state):
        len_row = len(game_state)
        len_col = len(game_state[0])
        
        the_q = float('inf')
        
        for i in range(len_row):
            for j in range(len_col):

                if game_state[i][j] != oursweeper.TileStatus.FLAGGED.value:
                    continue
                    
                game_state[i][j] = oursweeper.TileStatus.COVERED.value

                conf_index = 9

                for u in [-1, 0, 1]:
                    for v in [-1, 0, 1]:
                        conf_index -= 1
                        
                        if u == v == 0 or not (0 <= i + u < len_row and 0 <= j + v < len_col):
                            continue

                        config = confms.get_conf_ult(i+u, j+v, conf_index, game_state, self.actions)
                            
                        if config in self.actions:
                            q_val = self.actions[config].Q
                            ucb = self.c * np.sqrt(np.log(self.t) / self.actions[config].count)
                            q_val += np.sign(q_val) * ucb
                                
                        else:
                            #q_val = -(1e10)
                            #q_val = self.safe_reward - self.c * np.sqrt(np.log(self.t))
                            if self.unseen_type == 0:
                                q_val = self.safe_reward
                            else:
                                q_val = self.safe_reward - self.c * np.sqrt(np.log(self.t)/self.max_count)

                        if q_val <= the_q:
                            coord = (i, j)
                            the_q = q_val
                            the_action = config

                game_state[i][j] = oursweeper.TileStatus.FLAGGED.value
        
        play = {}
        play['x'] = coord[0]
        play['y'] = coord[1]
        play['q'] = the_q
        play['type'] = 'safe'

        self.last_call = the_action

        return play
      
    def mind_play(self, play_result):
        conf = self.last_call
        reward = self.bomb_reward if play_result else self.safe_reward
        
        if conf not in self.actions:
            self.np_actions += 1
        
        past_q = self.actions[conf].Q

        self.actions[conf].count += 1
        self.actions[conf].Q += (1./self.actions[conf].count)*(reward - self.actions[conf].Q)
        
        new_q = self.actions[conf].Q
        
        if abs(past_q) == 1 and abs(new_q) != 1:
            self.np_actions -= 1

        self.max_count = max(self.max_count, self.actions[conf].count)

        self.last_call = None
    
    def mind_game(self, bomb_map):
        for conf, x, y in self.flag_plays:
            reward = self.bomb_reward if bomb_map[x][y] else self.safe_reward
            
            past_q = self.actions[conf].Q

            self.actions[conf].count += 1
            self.actions[conf].Q += (1./self.actions[conf].count)*(reward - self.actions[conf].Q)
            
            new_q = self.actions[conf].Q
            
            if abs(past_q) == 1 and abs(new_q) != 1:
                self.np_actions -= 1

            self.max_count = max(self.max_count, self.actions[conf].count)
        
        game_state = self.last_game_state
            
        len_row = len(game_state)
        len_col = len(game_state[0])

        for i in range(len_row):
            for j in range(len_col):

                if game_state[i][j] is not oursweeper.TileStatus.COVERED.value:
                    continue

                conf_index = 9

                for u in [-1, 0, 1]:
                    for v in [-1, 0, 1]:
                        conf_index -= 1

                        if u == v == 0 or not (0 <= i + u < len_row and 0 <= j + v < len_col):
                            continue
                            
                        #if game_state[i+u][j+v] == 10 and not bomb_map[i+u][j+v]:
                        #    continue

                        conf = confms.get_conf_ult(i+u, j+v, conf_index, game_state, self.actions)
                        
                        if conf not in self.actions:
                            self.np_actions += 1
                        
                        #print(i + conf_index//3, j + conf_index%3)
                            
                        reward = self.bomb_reward if bomb_map[i][j] else self.safe_reward
                        
                        past_q = self.actions[conf].Q

                        self.actions[conf].count += 1
                        self.actions[conf].Q += (1./self.actions[conf].count)*(reward - self.actions[conf].Q)
                        
                        new_q = self.actions[conf].Q
                        
                        if abs(past_q) == 1 and abs(new_q) != 1:
                            self.np_actions -= 1
        
        self.flag_plays = []
        self.last_call = None
        self.last_game_state = None
