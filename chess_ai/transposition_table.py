import chess
import chess.polyglot
import numpy as np

class Transposition_Table():
    def __init__(self, size):
        self.size = size
        self.basic_cache = {}

    def __getitem__(self, index):
        index = chess.polyglot.zobrist_hash(index)
        return self.basic_cache[index] if index in self.basic_cache else None

    def store(self, position, eval):
        zobrist = chess.polyglot.zobrist_hash(position)
        if len(self.basic_cache) > self.size:
            print('Trans Table is full!')
            return False
        elif zobrist not in self.basic_cache:
            self.basic_cache[zobrist] = eval
            if len(self.basic_cache) % 15000 == 0:
                print('cache size:', len(self.basic_cache))
        return True


