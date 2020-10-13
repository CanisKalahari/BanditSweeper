import numpy as np
import itertools as it
from pprint import pprint

def get_conf(i, j, game_state): # numbers count
    conf = [0]*9
    len_col = len(game_state)
    len_row = len(game_state[0])

    for u in [-1, 0, 1]:
        for v in [-1, 0, 1]:
            if u == 0 and v == 0:
                continue

            if i + u >= 0 and i + u < len_col and j + v >= 0 and j + v < len_row :
                aux = game_state[i+u][j+v] if game_state[i+u][j+v] != None else 0
                conf[aux] += 1
            else:
                conf[0] += 1

    return tuple(conf)
    
def get_conf_alt(i, j, game_state, Q):
    conf = [0]*8 # 0 is top left
    len_col = len(game_state)
    len_row = len(game_state[0])
    
    t = 0
    
    for u in [-1, 0, 1]:
        for v in [-1, 0, 1]:
            if u == 0 and v == 0:
                continue
                
            if i + u >= 0 and i + u < len_col and j + v >= 0 and j + v < len_row:
                conf[t] = game_state[i+u][j+v] if game_state[i+u][j+v] != None else 0
            else:
                conf[t] = 0
                
            t += 1
            
    # Symmetry test
    
    if tuple(conf) not in Q:
        for u in range(1, 8):
            k = conf[-u:] + conf[:-u]
            
            if tuple(k) in Q:
                return tuple(k)
            
            k.reverse()
            
            if tuple(k) in Q:
                return tuple(k)
            
    return tuple(conf)

def get_conf_dumb(i, j, game_state):
    conf = [0]*9
    
    len_col = len(game_state)
    len_row = len(game_state[0])
    
    for u in [-1, 0, 1]:
        for v in [-1, 0, 1]:
            if u == 0 and v == 0:
                continue
                
            if i + u >= 0 and i + u < len_col and j + v >= 0 and j + v < len_row:
                aux = game_state[i+u][j+v] if game_state[i+u][j+v] != None else 0
                conf[aux] = 1
            else:
                conf[0] = 1
    
    return tuple(conf)

#esse cara aqui em baixo Ã©o decorator
#@profile
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

def get_conf_ult_old(i, j, conf_index, game_state, actions):
    conf = [0]*9
    
    len_row = len(game_state)
    len_col = len(game_state[0])
    
    for t, (u, v) in enumerate(it.product(range(-1,2), repeat=2)):
        if 0 <= i + u < len_row and 0 <= j + v < len_col:
            conf[t] = game_state[i+u][j+v]
        else:
            conf[t] = -1
    
    ci_matrix = [2, 5, 8, 1, 4, 7, 0, 3, 6]
    
    if conf_index == 2 or conf_index == 5: # 1 Rot
        conf = [conf[i] for i in ci_matrix]
    elif conf_index == 7 or conf_index == 8: # 2 Rot
        conf = conf[::-1]
    elif conf_index == 3 or conf_index == 6: # 3 Rot
        conf = [conf[i] for i in reversed(ci_matrix)]
    
    conf_index %= 2
    conf.append(conf_index)
    
    if tuple(conf) in actions:
        return tuple(conf)
    
    if conf_index == 0:
        conf[1], conf[2], conf[3], conf[5], conf[6], conf[7] = conf[3], conf[6], conf[1], conf[7], conf[2], conf[5]
        
        return tuple(conf)
        
    conf[0], conf[2], conf[3], conf[5], conf[6], conf[8] = conf[2], conf[0], conf[5], conf[3], conf[8], conf[6]
    return tuple(conf)
