import chess
import chess.polyglot
import numpy as np


class Entry:
    def __init__(self,val, flag, entry_depth, move):
        self.val = val
        self.flag = flag
        self.entry_depth = entry_depth
        self.move = move


class TranspositionTable:
    def __init__(self, size):
        self.size = size
        self.basic_cache = {}
        #self.saved = 0 #already in cache

    def __getitem__(self, position):
        #index =
        return self.basic_cache.get(chess.polyglot.zobrist_hash(position), None)

    def store(self, position, value, flag, entry_depth, move):
        #zobrist = chess.polyglot.zobrist_hash(position)
        if len(self.basic_cache) > self.size:
            print('Trans Table is full!')
            return False
        #elif zobrist not in self.basic_cache:
        self.basic_cache[chess.polyglot.zobrist_hash(position)] = Entry(value, flag, entry_depth, move)
        if len(self.basic_cache) % 15000 == 0:
            print('cache size:', len(self.basic_cache))
        # else:
        #     self.basic_cache[zobrist] = Entry(value, flag, entry_depth)
            #print('mistake! already in cache'),
            #raise Exception
            #self.saved+=1
            # if self.saved % 10000 == 0:
                #print('reoccurence:', self.saved)
        return True

    def empty_cache(self):
        self.basic_cache = {}

