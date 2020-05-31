import chess

# import tensorflow as tf
from timeit import default_timer as timer
from time import time
from transposition_table import TranspositionTable
import numpy as np
import random
from position_encoder import Position
from anytree import AnyNode, Node, RenderTree, AsciiStyle, LevelOrderGroupIter
from anytree.exporter import UniqueDotExporter
import sys
from tensorflow.keras import models
import pprint

# tf.enable_eager_execution()  # TF1; must be done before any model/tensor creation
# tf.compat.v1.disable_eager_execution()
# print(tf.__version__)

MOVE_VALUES = []
MOVE_SET = []

LOWER = -1
EXACT = 0
UPPER = 1

piece_names = {'N': 2, 'B': 3, 'R': 4, 'Q': 5, }

# based off ideas from chess programming wiki
piece_values = {
    # pawn
    1: 100,
    # bishop
    2: 300,
    # knight
    3: 300,
    # rook
    4: 500,
    # queen
    5: 900,
    # king
    6: 2000
}

piece_square_tables = {
    1: np.array([  # pawn
        0, 0, 0, 0, 0, 0, 0, 0,  # a1 - a8
        5, 10, 10, -20, -20, 10, 10, 5,  # b1 - b8
        5, -5, -10, 0, 0, -10, -5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, 5, 10, 25, 25, 10, 5, 5,
        10, 10, 20, 30, 30, 20, 10, 10,
        50, 50, 50, 50, 50, 50, 50, 50,
        0, 0, 0, 0, 0, 0, 0, 0
    ]),
    2: np.array([  # knight
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50
    ]),
    3: np.array([  # bishop
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -20, -10, -10, -10, -10, -10, -10, -20
    ]),
    4: np.array([  # rook
        0, 0, 0, 5, 5, 0, 0, 0,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        5, 10, 10, 10, 10, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0
    ]),
    5: np.array([  # queen
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -10, 5, 5, 5, 5, 5, 0, -10,
        0, 0, 5, 5, 5, 5, 0, -5,
        -5, 0, 5, 5, 5, 5, 0, -5,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20
    ]),
    6: np.array([  # king
        20, 30, 10, 0, 0, 10, 30, 20,
        20, 20, 0, 0, 0, 0, 20, 20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30
    ]),
    7: np.array([
        -50, -30, -30, -30, -30, -30, -30, -50,
        -30, -30, 0, 0, 0, 0, -30, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -20, -10, 0, 0, -10, -20, -30,
        -50, -40, -30, -20, -20, -30, -40, -50

    ])
}

model = models.load_model('model-12x8x8')


class Node_:
    def __init__(self, move, depth, val=None):
        self.move = move
        self.depth = depth
        self.val = val
        self.children = []

    def __repr__(self):
        return self.move + ' : ' + f'{self.val:.3f}, ' + f'{len(self.children)} children'

    def add_child(self, node):
        self.children.append(node)

    def set_val(self, val):
        self.val = val


class MinMaxTree:
    PATH = {}

    def __init__(self, root, turn):
        self.root = root
        self.turn = turn

    def _traverse(self, node, turn, move_list):
        if len(node.children) == 0:
            return node.val

        best_move = None
        if turn:
            max_val = -1.001
            for child in node.children:
                val = self._traverse(child, not turn, move_list)
                if val > max_val:
                    max_val = val
                    best_move = child.move
            move_list.append((f'{max_val:.3f}', best_move))
            return max_val
        else:
            min_val = 1.001
            for child in node.children:
                val = self._traverse(child, turn, move_list)
                if val < min_val:
                    min_val = val
                    best_move = child.move
            move_list.append((f'{min_val:.3f}', best_move))
            return min_val

    def print_best_path(self):
        move_list = []
        res = self._traverse(self.root, self.turn, move_list)
        print(move_list)


class ChessEngine:
    def __init__(self, fen=None, cache_size = 1e7):
        self.p_encoder = Position()
        self.board = chess.Board(fen) if fen else chess.Board()
        self.ttable = TranspositionTable(cache_size)
        self.MOVE_VAL = []
        self.X = 0

    def reset(self, fen=None):
        self.board = chess.Board()

    def get_results(self):
        res = self.board.result()
        if res == '0-1':
            return -1.0
        elif res == '1-0':
            return 1.0
        return 0.0

    def nn_eval(self):
        # return random.uniform(-1.0, 1.0)
        return model.predict(np.asarray([self.p_encoder.binary_encode(self.board)]))[0, 0]

    def conventional_eval(self):

        # TODO enable 3fold rep/50 move rule by improving client-server interaction
        white_val, black_val = 0, 0
        for piece in range(1, 7):
            white_piece = self.board.pieces(piece, True)
            back_piece = self.board.pieces(piece, False)
            white_arr = piece_square_tables[piece][np.array(list(white_piece))] if len(white_piece) > 0 else 0
            black_arr = piece_square_tables[piece][-(np.array(list(back_piece)) + 1)] if len(back_piece) > 0 else 0
            white_val += (np.sum(white_arr) + len(white_piece) * piece_values[piece])
            black_val -= (np.sum(black_arr) + len(back_piece) * piece_values[piece])

        val = (white_val + black_val) / 3500 #normalize between -1, 1
        if val > 1.0:
            val = 1.0
        elif val < -1.0:
            val = -1.0
        return val

    def move(self, san):
        self.board.push_san(san)

    def _move(self, san):
        self.board.push(san)

    def reset_X(self):
        self.X = 0

    def clear_move_list(self):
        self.MOVE_VAL.clear()

    def take_back(self):
        self.board.pop()
        if not self.board.turn:
            self.board.pop()

    def move_order(self, root, depth):
        move_order = []
        node = root
        turn = self.board.turn
        for i in range(depth):
            if len(node.children) == 0:
                return move_order
            # node = sorted(node.children, key = lambda x: x.val, reverse = turn)[0]
            # o(n) time instead of sorting
            nodes = np.array([[n.val, n] for n in node.children])
            best = nodes[np.argmax(nodes[:, 0])] if turn else nodes[np.argmin(nodes[:, 0])]
            move_order.append((round(best[0], 4), best[1].name))
            turn = not turn
            node = best[1]
        return move_order

    def computer_move(self, depth=4, verbose='n', depth_to_sort=1, nn=False):
        if 't' in verbose:
            root = Node('root', depth=0, val=None, no=0)
            self.min_max_tree_alpa_beta_nodes2(-1.0, 1.0, depth, 1, depth, root)
            move_order = self.move_order(root, depth)
            print(move_order)
            if verbose == 't+':
                for row in RenderTree(root,
                                      childiter=lambda x: sorted(x, key=lambda y: y.val, reverse=self.board.turn)):
                    print("%s%d %s %.3f" % (row.pre, row.node.no, row.node.name, row.node.val))
            # print(RenderTree(root))
            # UniqueDotExporter(root, indent=4, nodeattrfunc=lambda node:
            # 'label="%s. %s = %.3f"' % (str(node.no), node.name, node.val)).to_picture("udo.pdf")
            if len(self.MOVE_VAL) == 1:
                val = self.MOVE_VAL[0]
                self.clear_move_list()
                data = {'move': val[0], 'eval': val[1], 'moveOrder': move_order, 'num_pred': self.X}
                self.reset_X()
                self.move(val[0])
                return data
            return None
        else:
            moves, val = self.iterative_deepening_cache(depth, depth_to_sort, nn)
            if moves:
                print(moves)
                data = {'move': self.board.san(moves[-1]), 'eval': -val, 'num_pred': self.X}
                self.reset_X()
                self._move(moves[-1])
                return data
            return None


    def attacked_by_inferior_piece(self, move, sqr):
        m = self.board.san(move)
        for square in self.board.attackers(not self.board.turn, sqr):
            piece = self.board.piece_type_at(square)
            if m[0] in 'BN' and piece == chess.PAWN:
                return True
            elif m[0] == 'R' and (piece == chess.PAWN or piece == chess.BISHOP or piece == chess.KNIGHT):
                return True
            elif m[0] == 'Q' and (piece == chess.PAWN or piece == chess.BISHOP or piece == chess.KNIGHT
                                  or piece == chess.ROOK):
                return True
        return False

    def num_defenders_to_square(self, move):
        return len(self.board.attackers(self.board.turn, move.to_square))

    def num_attackers_to_square(self, move):
        return len(self.board.attackers(not self.board.turn, move.to_square))

    def sort_moves(self):
        legals = []
        post_smart = 0
        for move in self.board.legal_moves:
            m = self.board.san(move)
            # checks if move is checkmate
            if m[-1] == '#':
                return [move]
            # check capture moves
            if 'x' in m:
                # checks if move is a pawn capture, probably a good move
                if m[0].islower():
                    legals.insert(0, move)
                    post_smart += 1
                    continue
                # takes undefended piece, probably a good move
                elif not self.board.is_attacked_by(not self.board.turn, move.to_square):
                    legals.insert(0, move)
                    post_smart += 1
                    continue
                else:
                    legals.insert(post_smart, move)
                    continue

            # checks bad queen moves
            if m[0] == 'Q':
                # check if queen going to square controlled by other player, probably a bad move
                if self.board.is_attacked_by(not self.board.turn, move.to_square):
                    legals.append(move)
                    continue
                else:
                    legals.insert(post_smart, move)
                    continue

            # check if current piece being moved is being attacked by a piece inferior to it and if so,
            # is it being moved to a place where an inferior piece will attack it
            elif self.attacked_by_inferior_piece(move, move.from_square):
                # piece moves to square where different inferior piece is attacking it probably bad move
                if self.attacked_by_inferior_piece(move, move.to_square):
                    legals.append(move)
                    continue
                else:
                    # check square that piece is going to is defended more than attacked - probably a good move
                    if self.num_defenders_to_square(move) >= self.num_attackers_to_square(move):
                        legals.insert(0, move)
                        post_smart += 1
                        continue
                    # if more attackers than defenders, probably a bad move
                    else:
                        legals.append(move)
                        continue
            # piece moves to square where inferior piece is attacking it probably bad move
            elif self.attacked_by_inferior_piece(move, move.to_square):
                legals.append(move)
                continue

            # TODO check bad moves of other pieces
            legals.insert(post_smart, move)

        return legals

    def store_in_table(self, val, flag, depth_, move):
        return self.ttable.store(self.board, val, flag, depth_, move)

    def get_from_table(self):
        res = self.ttable[self.board]
        return res if res else None

    def empty_table(self):
        self.ttable.empty_cache()

    def iterative_deepening_cache(self, depth, depth_to_sort, nn=False):
        moves, val_ = self.negamax_cache(-1.0, 1.0, 1, None, 1, depth_to_sort, None, nn)
        for i in range(2, depth + 1):
            moves, val_ = self.negamax_cache(-1.0, 1.0, i, None, i, depth_to_sort, moves, nn)
        return moves, val_

    def iterative_deepening(self, depth, depth_to_sort):
        moves, val_ = self.negamax_it_deep(-1.0, 1.0, 1, None, 1, depth_to_sort, None)
        for i in range(2, depth + 1):
            moves, val_ = self.negamax_it_deep(-1.0, 1.0, i, None, i, depth_to_sort, moves)
        return moves, val_

    def negamax_cache(self, alpha, beta, depth, move, original_depth, depth_to_sort, prev_moves, nn):
        self.X += 1
        move_set = []
        alpha_orig = alpha
        color = 1 if self.board.turn else -1
        if self.board.is_game_over(claim_draw=False):
            move_set.append(move)
            return move_set, self.get_results() * color

        cached = self.get_from_table()
        if cached and cached.entry_depth >= depth:
            if cached.flag == EXACT:
                move = cached.move if not move else move
                move_set.append(move)
                return move_set, cached.val
            elif cached.flag == LOWER:
                alpha = max(alpha, cached.val)
            elif cached.flag == UPPER:
                beta = min(beta, cached.val)
            if alpha >= beta:
                move = cached.move if not move else move
                move_set.append(move)
                return move_set, cached.val

        if depth == 0:
            move_set.append(move)
            val = self.nn_eval() if nn else self.conventional_eval()
            return move_set, val * color
        best_move = None
        max_val = -1.0

        if original_depth - depth < depth_to_sort:
            legals = self.sort_moves()
        else:
            legals = list(self.board.legal_moves)

        if prev_moves and len(prev_moves) >= depth and prev_moves[depth - 1] in legals:
            legals.insert(0, prev_moves[depth - 1])

        for m in legals:
            self.board.push(m)
            new_move_set, pred_eval = self.negamax_cache(-beta, -alpha, depth - 1, m, original_depth, depth_to_sort,
                                                         prev_moves, nn)
            pred_eval = -pred_eval
            self.board.pop()
            if pred_eval > max_val:
                move_set = new_move_set
                max_val, best_move = pred_eval, m

            alpha = max(max_val, alpha)
            if alpha >= beta:
                break
        if max_val <= alpha_orig:
            flag = UPPER
        elif max_val >= beta:
            flag = LOWER
        else:
            flag = EXACT

        if not best_move: best_move = m
        self.store_in_table(max_val, flag, depth, best_move)
        move_set.append(best_move)
        return move_set, max_val

    def negamax_it_deep(self, alpha, beta, depth, move, original_depth, depth_to_sort, prev_moves):
        self.X += 1
        move_set = []
        color = 1 if self.board.turn else -1
        if self.board.is_game_over(claim_draw=False):
            move_set.append(move)
            return move_set, self.get_results() * color
        if depth == 0:
            move_set.append(move)
            return move_set, self.conventional_eval() * color
        best_move = None
        max_val = -1.0

        if original_depth - depth < depth_to_sort:
            legals = self.sort_moves()
        else:
            legals = list(self.board.legal_moves)

        if prev_moves and len(prev_moves) >= depth and prev_moves[depth - 1] in legals:
            legals.insert(0, prev_moves[depth - 1])

        for m in legals:
            self.board.push(m)
            new_move_set, pred_eval = self.negamax_it_deep(-beta, -alpha, depth - 1, m, original_depth, depth_to_sort,
                                                           prev_moves)
            pred_eval = -pred_eval
            self.board.pop()
            if pred_eval > max_val:
                move_set = new_move_set
                max_val, best_move = pred_eval, m

            alpha = max(max_val, alpha)
            if alpha >= beta:
                break
        if not best_move: best_move = m
        move_set.append(best_move)
        return move_set, max_val

    def negamax(self, alpha, beta, depth, original_depth, depth_to_sort):
        self.X += 1
        alpha_orig = alpha

        color = 1 if self.board.turn else -1
        if self.board.is_game_over(claim_draw=False):
            return self.get_results() * color

        cached = self.get_from_table()
        if cached and cached.entry_depth >= depth:
            if cached.flag == EXACT:
                return cached.val
            elif cached.flag == LOWER:
                alpha = max(alpha, cached.val)
            elif cached.flag == UPPER:
                beta = min(beta, cached.val)
            if alpha >= beta:
                return cached.val

        if depth == 0:
            return self.conventional_eval() * color
        best_move = None
        max_val = -1.0
        if original_depth - depth < depth_to_sort :
            legals = self.sort_moves()
        else:
            legals = self.board.legal_moves
        for move in legals:
            self.board.push(move)
            pred_eval = -self.negamax(-beta, -alpha, depth - 1, original_depth, depth_to_sort)
            self.board.pop()
            if pred_eval > max_val:
                max_val = pred_eval
                best_move = move
            alpha = max(max_val, alpha)
            if alpha >= beta:
                break
        if depth == original_depth:
            if not best_move: best_move = move
            self.MOVE_VAL.append((self.board.san(best_move), max_val * color))
        if max_val <= alpha_orig:
            flag = UPPER
        elif max_val >= beta:
            flag = LOWER
        else:
            flag = EXACT

        self.store_in_table(max_val, flag, depth)
        return max_val

    def min_max_tree_alpa_beta_fast(self, alpha, beta, depth, original_depth, depth_to_sort):
        self.X += 1
        if self.board.is_game_over(claim_draw=False):
            return self.get_results()
        if depth == 0:
            return self.conventional_eval()
        best_move = None
        if original_depth - depth < depth_to_sort :
            legals = self.sort_moves()
        else:
            legals = self.board.legal_moves

        if self.board.turn:
            minmax = -1.0
            for move in legals:
                self.board.push(move)

                pred_eval = self.min_max_tree_alpa_beta_fast(alpha, beta, depth - 1, original_depth, depth_to_sort)
                self.board.pop()

                if pred_eval > minmax:
                    minmax, best_move = pred_eval, move

                alpha = max(pred_eval, alpha)
                if alpha >= beta:
                    break
            if depth == original_depth:
                if not best_move: best_move = move
                self.MOVE_VAL.append((self.board.san(best_move), minmax))
        else:
            minmax = 1.0
            for move in legals:
                self.board.push(move)
                pred_eval = self.min_max_tree_alpa_beta_fast(alpha, beta, depth - 1, original_depth, depth_to_sort)
                self.board.pop()
                if pred_eval < minmax:
                    minmax, best_move = pred_eval, move
                beta = min(pred_eval, beta)
                if alpha >= beta:
                    break
            if depth == original_depth:
                if not best_move: best_move = move
                self.MOVE_VAL.append((self.board.san(best_move), minmax))
        return minmax

    def min_max_tree_alpa_beta_nodes2(self, alpha, beta, depth, opst_depth, original_depth, node):
        self.X += 1
        if self.board.is_game_over():
            res = self.get_results()
            node.val = res
            return res
        if depth == 0:
            eval_ = self.conventional_eval()
            node.val = eval_
            return eval_
        best_move = None
        if depth == original_depth:
            leg = self.sort_moves()
        else:
            leg = self.board.legal_moves
        if self.board.turn:
            max_eval = -1.0
            for move in leg:

                new_node = Node(self.board.san(move), parent=node, depth=opst_depth, val=None, no=self.X)
                self.board.push(move)
                pred_eval = self.min_max_tree_alpa_beta_nodes2(alpha, beta, depth - 1, opst_depth + 1, original_depth,
                                                               new_node)
                self.board.pop()

                if pred_eval > max_eval:
                    max_eval, best_move = pred_eval, move

                alpha = max(pred_eval, alpha)
                if alpha >= beta:
                    break
            if depth == original_depth:
                if not best_move: best_move = move
                self.MOVE_VAL.append((self.board.san(best_move), max_eval))
                node.name = 'root: best is ' + self.board.san(best_move)
            node.val = max_eval
            return max_eval
        else:
            min_eval = 1.0
            for move in leg:
                new_node = Node(self.board.san(move), parent=node, depth=opst_depth, val=None, no=self.X)
                self.board.push(move)
                pred_eval = self.min_max_tree_alpa_beta_nodes2(alpha, beta, depth - 1, opst_depth + 1, original_depth,
                                                               new_node)
                self.board.pop()
                if pred_eval < min_eval:
                    min_eval, best_move = pred_eval, move
                beta = min(pred_eval, beta)
                if alpha >= beta:
                    break

            if depth == original_depth:
                if not best_move: best_move = move
                self.MOVE_VAL.append((self.board.san(best_move), min_eval))
                node.name = 'root: best is ' + self.board.san(best_move)
            node.val = min_eval
            return min_eval


if __name__ == "__main__":

    FENS = [
        # '7k/8/8/3p4/8/8/3RBRB1/2KRQNNB b - - 0 1',
        # '7k/8/5K2/5P2/5P2/5P2/5P2/5PR1 w - - 0 1',
        # 'k7/6P1/1K6/8/8/8/8/8 w - - 0 1'
        # 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        # 'rnb1kbn1/1p1q4/8/p1N1p3/P3Kp2/5P2/1P6/8 w q - 1 24'
        # '8/5np1/4kb2/2Rr4/3B4/3KP3/4N3/8 w - - 0 1'
        # 'r1bqkbnr/pppppppp/2n5/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 1 2'
        # 'r2qk2r/pp1nppbp/6p1/1BpPn2b/4PB2/2N1QN1P/PPP2PP1/2KR3R w kq - 1 2'
        # '5k2/4P3/3K4/8/8/8/8/8 b - - 0 1'
        "8/8/P3R3/8/2b3K1/8/8/1k6 b - - 0 1"
        # "8/6pp/4P1pk/1p1P2p1/1P1p2P1/KP6/PP6/8 w - - 0 1"
        # rnbq1bn1/pppk1p2/3p1Pp1/3P2Q1/4N3/2P2B2/PP5P/2KRR3 w - - 3 26
    ]
    for i, fen in enumerate(FENS):
        print('position', i)
        depth = 2
        X = 0
        # print(MOVE_VALUES, positions_ab)
        # print(X - 1, 'number of predictions made\n')
        for d in range(1, 2):
            game = ChessEngine()
            game.move('e4')
            print('sorting depth:', d)
            start = timer()
            # alpha, beta, depth, move, original_depth, depth_to_sort
            moves, val = game.negamax_nocache(-1.0, 1.0, depth, None, depth, d)
            stop = timer()
            print(moves, val)
            print(stop - start, 'seconds')
            print(X - 1, 'number of predictions made\n')
