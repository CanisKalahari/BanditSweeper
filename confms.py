import numpy as np
import itertools as it
from pprint import pprint

def get_conf_ult(i, j, conf_index, game_state, actions):
    conf = [0]*9
    
    len_row = len(game_state)
    len_col = len(game_state[0])
    
    # Loop unrolling makes it extra fast
    if conf_index == 2 or conf_index == 5: # 1 Rot
        conf[0] = game_state[i-1][j+1] if 0 <= i-1 < len_row and 0 <= j+1 < len_col else -1
        conf[1] = game_state[i][j+1]   if 0 <= i   < len_row and 0 <= j+1 < len_col else -1
        conf[2] = game_state[i+1][j+1] if 0 <= i+1 < len_row and 0 <= j+1 < len_col else -1
        conf[3] = game_state[i-1][j]   if 0 <= i-1 < len_row and 0 <= j   < len_col else -1
        conf[4] = game_state[i][j]     if 0 <= i   < len_row and 0 <= j   < len_col else -1
        conf[5] = game_state[i+1][j]   if 0 <= i+1 < len_row and 0 <= j   < len_col else -1
        conf[6] = game_state[i-1][j-1] if 0 <= i-1 < len_row and 0 <= j-1 < len_col else -1
        conf[7] = game_state[i][j-1]   if 0 <= i   < len_row and 0 <= j-1 < len_col else -1
        conf[8] = game_state[i+1][j-1] if 0 <= i+1 < len_row and 0 <= j-1 < len_col else -1
    elif conf_index == 7 or conf_index == 8: # 2 Rot
        conf[0] = game_state[i+1][j+1] if 0 <= i+1 < len_row and 0 <= j+1 < len_col else -1
        conf[1] = game_state[i+1][j]   if 0 <= i+1 < len_row and 0 <= j   < len_col else -1
        conf[2] = game_state[i+1][j-1] if 0 <= i+1 < len_row and 0 <= j-1 < len_col else -1
        conf[3] = game_state[i][j+1]   if 0 <= i   < len_row and 0 <= j+1 < len_col else -1
        conf[4] = game_state[i][j]     if 0 <= i   < len_row and 0 <= j   < len_col else -1
        conf[5] = game_state[i][j-1]   if 0 <= i   < len_row and 0 <= j-1 < len_col else -1
        conf[6] = game_state[i-1][j+1] if 0 <= i-1 < len_row and 0 <= j+1 < len_col else -1
        conf[7] = game_state[i-1][j]   if 0 <= i-1 < len_row and 0 <= j   < len_col else -1
        conf[8] = game_state[i-1][j-1] if 0 <= i-1 < len_row and 0 <= j-1 < len_col else -1
    elif conf_index == 3 or conf_index == 6: # 3 Rot
        conf[0] = game_state[i+1][j-1] if 0 <= i+1 < len_row and 0 <= j-1 < len_col else -1
        conf[1] = game_state[i][j-1]   if 0 <= i   < len_row and 0 <= j-1 < len_col else -1
        conf[2] = game_state[i-1][j-1] if 0 <= i-1 < len_row and 0 <= j-1 < len_col else -1
        conf[3] = game_state[i+1][j]   if 0 <= i+1 < len_row and 0 <= j   < len_col else -1
        conf[4] = game_state[i][j]     if 0 <= i   < len_row and 0 <= j   < len_col else -1
        conf[5] = game_state[i-1][j]   if 0 <= i-1 < len_row and 0 <= j   < len_col else -1
        conf[6] = game_state[i+1][j+1] if 0 <= i+1 < len_row and 0 <= j+1 < len_col else -1
        conf[7] = game_state[i][j+1]   if 0 <= i   < len_row and 0 <= j+1 < len_col else -1
        conf[8] = game_state[i-1][j+1] if 0 <= i-1 < len_row and 0 <= j+1 < len_col else -1
    elif conf_index == 0 or conf_index == 1: # 0 Rot
        for t, (u, v) in enumerate(it.product(range(-1,2), repeat=2)):
            if 0 <= i + u < len_row and 0 <= j + v < len_col:
                conf[t] = game_state[i+u][j+v]
            else:
                conf[t] = -1
                
    conf_index %= 2
    conf.append(conf_index)
        
    if tuple(conf) in actions:
        return tuple(conf)
    
    if conf_index == 0:
        conf[1], conf[2], conf[3], conf[5], conf[6], conf[7] = conf[3], conf[6], conf[1], conf[7], conf[2], conf[5]
        
        return tuple(conf)
        
    conf[0], conf[2], conf[3], conf[5], conf[6], conf[8] = conf[2], conf[0], conf[5], conf[3], conf[8], conf[6]
    return tuple(conf)
