import numpy as np
import itertools as it
from pprint import pprint

def get_conf_ult(i, j, conf_index, game_state, actions):
    conf = [0]*9
    
    len_row = len(game_state)
    len_col = len(game_state[0])
    
    for t, (u, v) in enumerate(it.product(range(-1,2), repeat=2)):
        if 0 <= i + u < len_row and 0 <= j + v < len_col:
            conf[t] = game_state[i+u][j+v]
        else:
            conf[t] = -1
    
    ci_matrix = [2, 5, 8, 1, 4, 7, 0, 3, 6]
    
    if conf_index == 2 or conf_index == 5: # 1 Rotation
        conf = [conf[i] for i in ci_matrix]
    elif conf_index == 7 or conf_index == 8: # 2 Rotations
        conf = conf[::-1]
    elif conf_index == 3 or conf_index == 6: # 3 Rotations
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

def get_conf_ult_old(i, j, conf_index, game_state, actions): # Inefficient
    conf = [0]*9
    
    len_row = len(game_state)
    len_col = len(game_state[0])
    
    t = 0
    
    for u in [-1, 0, 1]:
        for v in [-1, 0, 1]:
            if 0 <= i + u < len_row and 0 <= j + v < len_col:
                conf[t] = game_state[i+u][j+v]
            else:
                conf[t] = -1
            
            t += 1
    
    aux_index = conf_index%2
    aux = [0]*9
    
    ci_matrix = [2, 5, 8, 1, 4, 7, 0, 3, 6]
    
    if conf_index == 0 or conf_index == 1:
        for i in range(9):
            aux[i] = conf[i]
    elif conf_index == 2 or conf_index == 5: # 1 Rot
        for i, j in enumerate(ci_matrix):
            aux[i] = conf[j]
       
    elif conf_index == 7 or conf_index == 8: # 2 Rot
        for i in range(9):
            aux[i] = conf[8-i]
       
    elif conf_index == 3 or conf_index == 6: # 3 Rot
        for i in range(9):
            aux[i] = conf[ci_matrix[8-i]]
    
    aux.append(aux_index)
    
    if tuple(aux) in actions:
        return tuple(aux)
    
    if aux_index == 0:
        aux[1], aux[2], aux[3], aux[5], aux[6], aux[7] = aux[3], aux[6], aux[1], aux[7], aux[2], aux[5]
        
        return tuple(aux)
        
    elif aux_index == 1:
        aux[0], aux[2], aux[3], aux[5], aux[6], aux[8] = aux[2], aux[0], aux[5], aux[3], aux[8], aux[6]
        
        return tuple(aux)
