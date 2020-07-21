import argparse
import os.path
import pickle
import random
import sys
import time

from pprint import pprint

import minesweeper
import players

SEP = ','
min_game_p = 1.

def load_player(player_str):
    if os.path.isfile(f'./Pickles/{player_str}_player.pickle'):
        pickle_in = open(f'./Pickles/{player_str}_player.pickle',"rb")
        player = pickle.load(pickle_in)
        
    else:
        player_type = player_str.split(SEP)[0]
        player_args = player_str.split(SEP)[1:]

        if player_type == 'megreedy':
            E, F, safe_reward, bomb_reward, unseen_q = map(float, player_args)
            player = players.MegreedyPlayer(E, F, safe_reward, bomb_reward, unseen_q)
        elif player_type == 'mucb':
            c, safe_reward, bomb_reward, unseen_type = map(float, player_args)
            player = players.MUCBPlayer(c, safe_reward, bomb_reward, unseen_type)
        else:
            raise Exception('Error 404: player not found')

    return player

def parse_settings(arg_str):    
    arg_list = arg_str.split(SEP)
    
    width = int(arg_list[0])
    height = int(arg_list[1])
    
    mine_list = arg_list[2:]
    
    return [minesweeper.GameConfig(width, height, int(aux)) for aux in mine_list]

def get_valid_game(game_config): # This enforces the rule making the first click always be a blank tile
    game = minesweeper.Game(game_config)
    
    for y in range(game_config.height):
        for x in range(game_config.width):
            if not game.board[x][y] and game.counts[x][y] == 0:
                game.select(x, y)
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

    player = load_player(args.player)
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

            flags = 0       # Counter for flag plays
            safes = 1       # Counter for safe plays (starts with 1 as first play is always safe)
            min_q = abs(player.safe_reward)     # Minimum chosen action-value
            sum_q = 0               # Sum of all values of actions played
            last_q = player.safe_reward     # Last action-value seen

            game = get_valid_game(game_config)
            player.last_game_state = game.get_state()

            while not game.is_game_over():
                play = player.call_play(game.get_state())

                sum_q += play['q']
                min_q = min(min_q, play['q'])
                last_q = play['q']

                if play['type'] == 'flag':
                    flags += 1

                    if game.set_flag(play['x'], play['y']):
                        play = player.pick_flag(game.get_state())
                        game.unset_flag(play['x'], play['y'])
                    else:
                        continue
                else:
                    if (play['x'], play['y']) in game.flags:
                        game.unset_flag(play['x'], play['y'])

                    safes += 1

                play_result = game.select(play['x'], play['y'])

                player.mind_play(play_result)

            num_wrong_flags = player.mind_game(game.board)
            pbc = game.num_exposed_squares/game.num_safe_squares # pbc = percentage board clear

            got_win = not game.explosion

            avg_q = sum_q / (safes + flags)
            game_stats = [got_win, safes, flags, min_q, avg_q, last_q, len(player.actions), num_wrong_flags, pbc, player.np_actions]
            all_stats.append(game_stats)

            new_wc = win_count + got_win
            round_i += 2

            if abs((new_wc + 1)/(round_i + 1) - (win_count + 1)/round_i) < args.threshold:
                break

            win_count = new_wc
            
    if args.save or time.time() - timestamp > 15 * 60: 
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

    print('Time elapsed:', time.time() - timestamp)
    print('Rounds played:', len(all_stats))
    print('Recorded actions:', len(player.actions))
    print('Top10 actions')
    pprint(sorted(player.actions.items(), key=lambda x: (abs(x[1].Q), x[1].count), reverse=True)[:10])
    print('# perfect actions:', sum(abs(i[1].Q) == 1 for i in player.actions.items()), 'or', player.np_actions)

    print(f'Win rate: {100. * wr}%')
    
    return str(timestamp), 100. * wr

if __name__ == '__main__':
    #python3 experimento.py -p megreedy,0,0,-1,1,-1 -s 8,8,10 -r 1000000 -t 0 --save
    
    run_trial(None)
