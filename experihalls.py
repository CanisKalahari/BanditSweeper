import argparse
import os.path
import pickle
import random
import sys
import time

from pprint import pprint

import oursweeper
import ourplayers

SEP = ','
min_game_p = 1.

def here_comes_a_new_challenger(player_str):
    if os.path.isfile(f'./Pickles/{player_str}_player.pickle'):
        pickle_in = open(f'./Pickles/{player_str}_player.pickle',"rb")
        player = pickle.load(pickle_in)
        
    else:
        player_type = player_str.split(SEP)[0]
        player_args = player_str.split(SEP)[1:]

        if player_type == 'dummy':
            player = ourplayers.DummyPlayer(player_args)
        elif player_type == 'megreedy':
            E, F, safe_reward, bomb_reward, unseen_q = map(float, player_args)
            player = ourplayers.MegreedyPlayer(E, F, safe_reward, bomb_reward, unseen_q)
        elif player_type == 'mucb':
            c, safe_reward, bomb_reward, unseen_type = map(float, player_args)
            player = ourplayers.MUCBPlayer(c, safe_reward, bomb_reward, unseen_type)
        elif player_type == 'knn':
            K, safe_reward, bomb_reward = map(float, player_args)
            player = ourplayers.KNNPlayer(int(K), safe_reward, bomb_reward)
        else:
            raise Exception('Error 404: player not found')

    return player

def parse_settings(arg_str):
    arg_list = arg_str.split(SEP)
    
    width = int(arg_list[0])
    height = int(arg_list[1])
    
    mine_list = arg_list[2:]
    
    return [(height, width, int(aux)) for aux in mine_list]

def get_valid_game(game_config):
    game = oursweeper.Game(*game_config)
    
    for y in range(game.n_rows):
        for x in range(game.n_cols):
            if not game.is_mine(x,y) and game.tile_num[x][y] == 0:
                game.click(x, y)
                return game
            
    return game

def run_trial(arg_list):
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--rounds', type=int, default=10**6)
    parser.add_argument('-t', '--threshold', type=float, nargs='?', const=1e-6, default=1e-12)
    parser.add_argument('-p', '--player', required=True)
    parser.add_argument('-s', '--settings', required=True)
    parser.add_argument('-S', '--save', action='store_true')

    args = parser.parse_args(arg_list)

    timestamp = time.time()

    player = here_comes_a_new_challenger(args.player)
    game_config_list = parse_settings(args.settings)

    all_stats = []
    
    for game_config in game_config_list:
        win_count = 0

        round_start = time.time()

        for round_i in range(args.rounds):
            if round_i % 10**4 == 1:
                cur_time = time.time()
                elapsed = cur_time - round_start
                to_end = elapsed * (args.rounds - round_i) / round_i
                print(round_i, win_count/round_i, to_end, file=sys.stderr)

            flags = 0       # contadores
            safes = 1       # safes = 1 pq primeiro click é sempre safe
            min_q = abs(player.safe_reward)     # menor q_val numa jogada feita
            sum_q = 0               # soma dos q_val de todas jogadas feitas
            last_q = player.safe_reward     # Ultimo q_val visto

            #LET'S PLAY BALL!

            game = get_valid_game(game_config)
            player.last_game_state = game.get_board()

            while not game.is_over():
                play = player.call_play(game.get_board())

                sum_q += play['q']
                min_q = min(min_q, play['q'])
                last_q = play['q']

                if play['type'] == 'flag':
                    flags += 1

                    if game.set_flag(play['x'], play['y']):
                        play = player.pick_flag(game.get_board())
                        game.remove_flag(play['x'], play['y'])
                    else:
                        continue
                else:
                    if game.tile_status[play['x']][play['y']] == oursweeper.TileStatus.FLAGGED:
                        game.remove_flag(play['x'], play['y'])

                    safes += 1

                play_result = game.click(play['x'], play['y'])

                player.mind_play(play_result)

            num_wrong_flags = player.mind_game(game.get_bomb_map())
            pbc = game.n_uncovered/(game.n_cols*game.n_rows - game.n_mines)

            got_win = game.status == oursweeper.GameStatus.WIN

            avg_q = sum_q / (safes + flags)
            game_stats = [got_win, safes, flags, min_q, avg_q, last_q, len(player.actions), num_wrong_flags, pbc, player.np_actions]
            all_stats.append(game_stats)

            new_wc = win_count + got_win
            round_i += 2

            #print(win_count, got_win, round_i, abs((new_wc+1)/(round_i+1)-(win_count+1)/round_i))

            if abs((new_wc + 1)/(round_i + 1) - (win_count + 1)/round_i) < args.threshold:
                break

            win_count = new_wc
            
    if args.save or time.time() - timestamp > 15 * 60:  #demorou mais que 15 minutos -> salva
        print(timestamp)

        sys.stdout = open(f'Pickles/{timestamp}_log.txt', 'w')

        if arg_list is None:
            print(' '.join(sys.argv[1:]))
        else:
            print(' '.join(arg_list))

        with open(f'Pickles/{timestamp}_stats.pickle', "wb") as pickle_out:
            pickle.dump(all_stats, pickle_out)

        with open(f'Pickles/{timestamp}_player.pickle', "wb") as pickle_out:
            pickle.dump(player, pickle_out)
            
    wr = sum(k[0] for k in all_stats) / len(all_stats)
            
    if True:# arg_list is None:

        print('Time elapsed:', time.time() - timestamp)
        print('Rounds played:', len(all_stats))
        print('Recorded actions:', len(player.actions))
        print('Top10 actions')
        pprint(sorted(player.actions.items(), key=lambda x: (abs(x[1].Q), x[1].count), reverse=True)[:10])
        print('# perfect actions:', sum(abs(i[1].Q) == 1 for i in player.actions.items()), 'or', player.np_actions)

        print(f'Win rate: {100. * wr}%')

    #import pdb; pdb.set_trace()
    
    return str(timestamp), 100. * wr

if __name__ == '__main__':
    #exemplo de chamada no terminal: python3 experimento.py -p megreedy,0,0,0,1 -s 5,5,4 -r 1000
    #python3 experimento.py -p mucb,.1,-1,1,-1 -s 5,5,4 -r 1000
    
    run_trial(None)
