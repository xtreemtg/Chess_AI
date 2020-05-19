import chess
import chess.pgn
from state import State
import numpy as np
import os
import re
from tqdm import tqdm

#https://www.pgnmentor.com/files.html#events



def get_pgn_list(file_name):
    try:
        file_ = open(file_name, 'r')
        whole = file_.read()
    except UnicodeDecodeError:
        file_ = open(file_name, 'r', encoding="ISO-8859-1")
        whole = file_.read()
    pgn_regex = r'\n\n\['
    chunks = re.split(pgn_regex, whole)
    for i, string in enumerate(chunks[1:]):
        chunks[i + 1] = '[' + string
    return chunks

def save_games(dir_name, game_dir_name, games):
    if not os.path.exists(f'{dir_name}/{game_dir_name}'):
        os.mkdir(f'{dir_name}/{game_dir_name}')
    for i, text in enumerate(games):
        file = open(f"./{dir_name}/{game_dir_name}/{game_dir_name}_{i}.pgn", "w")
        file.write(text)
        file.close()

def get_data():
    X, y = [], []
    for dirs in os.listdir("games")[2:]:
        if not 'DS_Store' in dirs:
            print(dirs)
            for games in os.listdir("games" + '/' + dirs):
                print(f'Parsing game: {games} in {dirs}, got {len(X)} positions')
                pgn = open(os.path.join("games" + '/' + dirs, games))
                game = chess.pgn.read_game(pgn)
                if not game :#or game.headers.get('Variant', 'Standard') != 'Standard':
                    continue
                try:
                    board = game.board()
                except ValueError as e:
                    print(e, games)
                    continue
                values = {'1/2-1/2': 0, '0-1': -1, '1-0': 1}
                res = game.headers['Result']
                if res not in values:
                    continue
                value = values[res]
                for i, move in enumerate(game.mainline_moves()):
                    ser = State(board).serialize()
                    board.push(move)
                    X.append(ser)
                    y.append(value)


    print(np.asarray(X).shape, np.asarray(y).shape)
    print('done')
    return X, y

def main():

    X, y = get_data()
    np.savez("grandmasters_dataset.npz", X, y)








main()
#
# wei_games = get_pgn_list('lichess_xtreemtg.pgn')
# save_games('games', 'Yonah', wei_games)
#
# wei_games = get_pgn_list('Wei.pgn')
# save_games('games', 'Wei', wei_games)
#
# wei_games = get_pgn_list('Carlsen.pgn')
# save_games('games', 'Carlsen', wei_games)
#
# wei_games = get_pgn_list('Caruana.pgn')
# save_games('games', 'Caruana', wei_games)