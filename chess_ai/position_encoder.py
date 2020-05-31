import chess
import numpy as np


class Position:
    def __init__(self, board=None):
        self.board = board if board else chess.Board()

    def binary_encode(self, board):
        assert self.board.is_valid()
        #board = self.board if not board else board
        state = np.zeros(768, np.uint8)
        x = 0
        for i in range(1, 7):
            idx = np.array(list(board.pieces(i, chess.WHITE))) + x
            if idx.size > 0:
                state[idx] = 1
            x += 64
        for i in range(1, 7):
            idx = np.array(list(board.pieces(i, chess.BLACK))) + x
            if idx.size > 0:
                state[idx] = 1
            x += 64

        # if board.ep_square and board.has_legal_en_passant():
        #     idx = board.ep_square + x
        #     state[idx] = 1
        #
        # state[-5] = int(board.turn)
        # state[-4] = int(board.has_kingside_castling_rights(chess.WHITE))
        # state[-3] = int(board.has_queenside_castling_rights(chess.WHITE))
        # state[-2] = int(board.has_kingside_castling_rights(chess.BLACK))
        # state[-1] = int(board.has_queenside_castling_rights(chess.BLACK))
        return state.reshape((12,8,8))

