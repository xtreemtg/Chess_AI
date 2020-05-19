import chess

# import tensorflow as tf
from timeit import default_timer as timer
from transposition_table import Transposition_Table
import numpy as np
import random
from state import State
import sys
# from tensorflow.keras import models
import pprint

# tf.enable_eager_execution()  # TF1; must be done before any model/tensor creation
# tf.compat.v1.disable_eager_execution()
# print(tf.__version__)

piece_values = {
    # pawn
    1: 1,
    # bishop
    2: 3,
    # knight
    3: 3,
    # rook
    4: 5,
    # queen
    5: 9,
    # king
    6: 100
}

ttable = Transposition_Table(1e7)

X = 0


# model = models.load_model('model2')


class Chess_Engine():
    def __init__(self, fen=None):
        self.s = State(chess.Board(fen)) if fen else None
        self.board = self.s.board if self.s else None

    def reset(self):
        self.__init__()

    # def set_state(self, state):
    #     self.s = state
    #     self.board = self.s.board

    def get_results(self):
        res = self.board.result()
        if res == '0-1':
            return -1.0
        elif res == '1-0':
            return 1.0
        elif res == '1/2-1/2':
            return 0.0

    def predict_eval(self):
        global X
        X += 1
        # return random.uniform(-1.0, 1.0)
        return model.predict(np.asarray([self.s.serialize()]))[0, 0]

    def conventional_eval(self):
        global X
        X += 1
        white_val, black_val = 0, 0
        for i in range(1, 7):
            white_val += len(self.board.pieces(i, True)) * piece_values[i]
            black_val += len(self.board.pieces(i, False)) * piece_values[i]
        return (white_val - black_val) / 140

    # def eval_leaves(self, moves):
    #     evals = []
    #     for move in moves:
    #         self.s.board.push(move)
    #         ser = self.s.serialize()
    #         eval = self.predict_eval(ser)
    #         evals.append((move, eval))
    #         self.s.board.pop()
    #     return evals
    #
    # def min_max_tree(self, depth=1):
    #     if depth == 1:
    #         return self.eval_leaves(self.s.legal_moves())

    # def random_move(self, verbose=True):
    #     moves = self.s.legal_moves()
    #     m = random.choice(moves)
    #     if verbose:
    #         print(self.s.board.san(m))
    #     self.s.board.push(m)

    def computer_move(self, depth=4, verbose=False):
        eval_moves = self.min_max_tree_alpa_beta([], -1.0, 1.0, depth, depth)
        best = sorted(eval_moves, key=lambda x: x[1], reverse=self.s.board.turn)[0][0]
        if verbose:
            print([(self.s.board.san(move[0]),move[1]) for move in eval_moves])
            print('best:',self.s.board.san(best))
        return self.s.board.san(best)

    # def is_game_over(self):
    #     return self.board.is_game_over()
    #
    # def push_san(self, move):
    #     self.board.push_san(move)

    def sort_moves(self):
        legals = [move for move in self.board.legal_moves]
        for i in range(len(legals)):
            # checks if move is a pawn capture
            if self.board.san(legals[i])[-1] == '#':
                legals.insert(0, legals.pop(i))
                return legals
            if self.board.san(legals[i])[0].islower() and self.board.is_capture(legals[i]):
                legals.insert(0, legals.pop(i))

        # for i in range(len(legals) - 1, -1, -1):
        #     # same with rook, knight and bishop but only when it doesn't capture anything
        #     if self.board.san(legals[i])[0] in 'RBN' and \
        #             self.board.is_attacked_by(not self.board.turn, legals[i].to_square) and \
        #             not self.board.is_capture(legals[i]) and \
        #             len(self.board.attackers(not self.board.turn, legals[i].to_square)) > \
        #             len(self.board.attackers(self.board.turn, legals[i].to_square)):
        #         legals.insert(len(legals), legals.pop(i))
        #     # puts queen going to dumb square in the back
        #     if self.board.san(legals[i])[0] == 'Q' and self.board.is_attacked_by(not self.board.turn,
        #                                                                          legals[i].to_square):
        #         legals.insert(len(legals), legals.pop(i))
        return legals

    def store_in_table(self, value):
        return ttable.store(self.board, value)

    def get_from_table(self):
        res = ttable[self.board]
        return res if res else None


    # def min_max_tree2(self, positions, depth=0, original_depth = 0):
    #     if self.board.is_game_over():
    #         return self.get_results()
    #     if depth == 0:
    #         return self.predict_eval()
    #     legal_moves = self.sort_moves()
    #     if self.board.turn:
    #         max_eval = -1.0
    #         for move in legal_moves:
    #             self.board.push(move)
    #             pred_eval = self.min_max_tree2(positions, depth - 1, original_depth)
    #             if depth == original_depth:
    #                 positions.append((move, pred_eval))
    #             self.board.pop()
    #             max_eval = max(max_eval, pred_eval)
    #         if depth == original_depth:
    #             return positions
    #         else: return max_eval
    #     else:
    #         min_eval = 1.0
    #         for move in legal_moves:
    #             self.board.push(move)
    #             pred_eval = self.min_max_tree2(positions, depth - 1, original_depth)
    #             if depth == original_depth:
    #                 positions.append((move, pred_eval))
    #             self.board.pop()
    #             min_eval = min(min_eval, pred_eval)
    #         if depth == original_depth:
    #             return positions
    #         else: return min_eval

    def min_max_tree_alpa_beta(self, positions, alpha, beta, depth=0, original_depth=0):
        #print(position, '\n')
        cached_val = self.get_from_table()
        if cached_val:
            return cached_val
        if self.board.is_game_over():
            global X
            X += 1
            res = self.get_results()
            if not self.store_in_table(res): sys.exit(0)
            return res
        if depth == 0:
            eval_ = self.conventional_eval()
            if not self.store_in_table(eval_): sys.exit(0)
            return eval_
        #legal_moves = self.sort_moves()
        legal_moves = self.board.legal_moves
        if self.board.turn:
            max_eval = -1.0
            for move in legal_moves:
                self.board.push(move)
                # cached_val = self.get_from_table()
                # if cached_val:
                #     pred_eval = cached_val
                # else:
                pred_eval = self.min_max_tree_alpa_beta(positions, alpha, beta, depth - 1, original_depth)
                if depth == original_depth:
                    positions.append((move, pred_eval))
                self.board.pop()
                max_eval = max(max_eval, pred_eval)
                alpha = max(alpha, pred_eval)
                if beta <= alpha:
                    break
            if depth == original_depth:
                return positions
            else:
                return max_eval
        else:
            min_eval = 1.0
            for move in legal_moves:
                self.board.push(move)
                # cached_val = self.get_from_table()
                # if cached_val:
                #     pred_eval = cached_val
                # else:
                pred_eval = self.min_max_tree_alpa_beta(positions, alpha, beta, depth - 1, original_depth)
                if depth == original_depth:
                    positions.append((move, pred_eval))
                self.board.pop()
                min_eval = min(min_eval, pred_eval)
                beta = min(beta, pred_eval)
                if beta <= alpha:
                    break
            if depth == original_depth:
                return positions
            else:
                return min_eval


if __name__ == "__main__":
    FENS = [
        # 'rnbqkbnr/ppppp3/8/4N3/2BP1BQ1/1r2P1Pp/PPP4P/RN2K2R b KQkq - 0 1',
        # '4k3/5P2/4K3/8/8/8/8/8 b - - 0 1',
        # 'r5k1/5ppp/1K6/PPP5/b7/B2R4/r2Q4/8 w - - 7 60',
        # 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        '2r1r1k1/1pq2ppp/p2bbp2/3p4/Q2P4/3B3P/PPP1NPP1/1R3RK1 w - - 1 17'
    ]
    for i, fen in enumerate(FENS):
        print('position', i)
        game = Chess_Engine(fen)
        depth = 6
        # start = timer()
        # positions = game.min_max_tree2([], depth, depth)
        # stop = timer()
        # print(stop - start)
        # pprint.pprint(positions)
        # global X
        X = 0

        start = timer()
        positions_ab = game.min_max_tree_alpa_beta([],-1.0,1.0, depth, depth)
        stop = timer()
        print(stop - start)
        pprint.pprint(positions_ab)
        print(X, 'number of predictions made\n')
