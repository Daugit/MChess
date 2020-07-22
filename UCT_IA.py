import copy
import random
from math import *
import time

import chess

BLACK = False
WHITE = True

d = {
    "a": 0,
    "b": 1,
    "c": 2,
    "d": 3,
    "e": 4,
    "f": 5,
    "g": 6,
    "h": 7,
    "8": 0,
    "7": 1,
    "6": 2,
    "5": 3,
    "4": 4,
    "3": 5,
    "2": 6,
    "1": 7
}


def add(board, h, Table):
    nplayouts = [0.0 for x in range(len([i for i in board.legal_moves]))]  # propre au board
    nwins = [0.0 for x in range(len([i for i in board.legal_moves]))]

    Table[h] = [1, nplayouts, nwins]


def look(h, Table):
    try:
        t = Table[h]
    except:
        t = None
    return t


def score(board):
    """
    Favoriser le noir

    :param board:
    :return:
    """
    return 1 if board.result(claim_draw=True) == "0-1" else 0


def playout(b, h, hashTable, hashTurn):
    start = time.time()
    while (True):
        moves = b.legal_moves
        moves = [i for i in moves]
        if b.is_game_over():
            # print(self.board, "\n")
            # print("PLAYOUT : ", time.time() - start)

            return score(b), h
        n = random.randint(0, len(moves) - 1)
        h = play(b, h, hashTable, hashTurn, moves[n])


def get_color_code(col):
    if (col == None):
        code = 0
    elif (col):
        code = 1
    else:
        code = 2
    return code


def update_hashcode(board, h, hashTable, hashTurn, move):
    """
    Update hashcode of a board.

    Need to call this function before using board.push(move).

    :param board:
    :param h:
    :param move:
    :return:
    """
    col = board.color_at(move.to_square)
    col = get_color_code(col)

    from_uci = chess.square_name(move.from_square)
    x1 = d[from_uci[0]]
    y1 = d[from_uci[1]]
    to_uci = chess.square_name(move.to_square)
    x2 = d[to_uci[0]]
    y2 = d[to_uci[1]]

    move_color = get_color_code(board.turn)

    if col != None:
        h = h ^ hashTable[col][x2][y2]

    h = h ^ hashTable[move_color][x2][y2]
    h = h ^ hashTable[move_color][x1][y1]
    h = h ^ hashTurn

    return h


def play(board, h, hashTable, hashTurn, best_move):
    h = update_hashcode(board, h, hashTable, hashTurn, best_move)
    board.push(best_move)

    return h


def UCT(board, h, hashTable, hashTurn, Table):
    if board.is_game_over():
        return score(board), h

    t = look(h, Table)
    if t != None:  # Selection and expansion step
        bestValue = -1000000.0
        best = 0

        moves = [i for i in board.legal_moves]
        if len(moves) != len(t[1]):
            print("Error : ", len(moves))
            print("Error : ", len(t[1]))
        for i in range(0, len(moves)):

            val = 1000000.0  # pour jouer tous les coups => ON VA JOUER TOUS LES COUPS DE PROFONDEUR 1??
            if t[1][i] > 0:
                Q = t[2][i] / t[1][i]
                if board.turn == WHITE:
                    Q = 1 - Q
                val = Q + 0.4 * sqrt(log(t[0]) / t[1][i])
            if val > bestValue:
                bestValue = val
                best = i

        res = 0.0
        if len(moves) > 0:
            h = update_hashcode(board, h, hashTable, hashTurn, moves[best])
            board.push(moves[best])
            res, h = UCT(board, h, hashTable, hashTurn, Table)
            t[0] += 1
            t[1][best] += 1  # mise à jour à l'indice best, qui est propre au board
            t[2][best] += res
        return res, h
    else:  # Sampling step
        add(board, h, Table)
        score_playout, h = playout(board, h, hashTable, hashTurn)
        return score_playout, h


def BestMoveUCT(board, h, hashTable, hashTurn, nb_playout):
    print("Starting calculating best move...")
    Table = {}

    for i in range(nb_playout):  # on met à jour la table de transposition avec les stats par coup legal
        b1 = copy.deepcopy(board)
        h1 = h
        UCT(b1, h1, hashTable, hashTurn, Table)
    t = look(h, Table)
    moves = [i for i in board.legal_moves]
    best = moves[0]
    bestValue = t[1][0]
    for i in range(0, len(moves)):
        if (t[1][i] > bestValue):
            bestValue = t[1][i]
            best = moves[i]
    print("Ending calculating best move...")
    return best