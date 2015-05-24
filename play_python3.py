
import sys
import random
import time
import copy
import os
from datetime import datetime
from pprint import pprint

import checkers

class event:
    def __init__(self, x, y):
        self.x = x
        self.y = y


RED = 1
BLACK = 2
RKING = 3
BKING = 4
KING = 2

EXTRA = 25
LOOK_AHEAD = 5
LOOK_AHEAD2 = 6
LOOK_AHEAD3 = 7
LOOK_AHEAD4 = 9

class CheckersAI(checkers.CheckersInterface):
    START_BOARD = [[0, RED, 0, RED, 0, RED, 0, RED],
                   [RED, 0, RED, 0, RED, 0, RED, 0],
                   [0, RED, 0, RED, 0, RED, 0, RED],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [BLACK, 0, BLACK, 0, BLACK, 0, BLACK, 0],
                   [0, BLACK, 0, BLACK, 0, BLACK, 0, BLACK],
                   [BLACK, 0, BLACK, 0, BLACK, 0, BLACK, 0]]
    aiPlaying = True
    look_ahead_val = LOOK_AHEAD
    all_moves = None
    multi_jump = None

    def __init__(self, numPlayers=1, playerName='Unidentified Player'):
        checkers.CheckersInterface.__init__(self)
        self.board = self.START_BOARD
        #self.ci = checkers.CheckersInterface(self.START_BOARD)
        self.boardSize = self.SQUARESIZE * 8
        if numPlayers == 2:
            self.aiPlaying = False;

        logfolder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logs')

        if not os.path.exists(logfolder):
            os.makedirs(logfolder)

        logfile = "game-%s.log" % datetime.now().strftime('%Y%m%d%H%M%S')
        self.logfile = os.path.join(logfolder, logfile)
        
        if numPlayers == 1:
            msg = '%s vs. AI Opponent, good luck!' % playerName
            with open(self.logfile, 'w') as out:
                pprint(msg, stream=out)


    def playGame(self):
        self.setup_move()

        while not self.GameDone():
            if self.end_now:
                break

            self.MoveLoop()

            if self.moving == 'black' and self.aiPlaying:
                self.ai_move()

        winner = 'Red'
        if self.GameDone() == BLACK:
            winner = 'Black'

        msg = '%s wins!' % winner
        pprint(msg)
        with open(self.logfile, 'a') as out:
            pprint(msg, stream=out)

        self.endGame()
        

    def ai_move(self):
        if self.multi_jump:
            bestMove = self.multi_jump
            bestMoveScore = 'multi'
            m2 = None
            time.sleep(1) # make sure board is updated
        else:
            moves, m2 = self.look_ahead(self.board, BLACK)

            if not moves:
                return

            bestMove = None
            bestMoveScore = None
            for mv, cdr in moves.items():
                if bestMoveScore == None or cdr[1] > bestMoveScore:
                    bestMoveScore = cdr[1]
                    bestMove = mv
            
            #self.printDebug(moves)              

        move = bestMove
        #pprint(m2)
        pprint("Best move: %s, score: %s"
               % (move, bestMoveScore))

        self.domove(move)

        # handle multi jumps
        if len(move) > 4:
            self.multi_jump = move[2:]
        else:
            self.multi_jump = None


    def domove(self, move):
        self.get_piece_click(event(move[1] * self.SQUARESIZE + EXTRA,
                                   move[0] * self.SQUARESIZE + EXTRA))
        time.sleep(.5)
        self.get_square_click(event(move[3] * self.SQUARESIZE + EXTRA,
                                    move[2] * self.SQUARESIZE + EXTRA))
        
    # NOTE: this function is taken from checkers.py and had to be overridden
    # to include my AI in the loop.x
    def MoveLoop(self):
        self.master.update()
        if self.got_move:
            if not self.check_move():
                # whenever a move is gotten which is correct, do this stuff
                self.do_move()
                self.cleanup_move(2)
                self.setup_move()
                self.cleanup_move(3)
            # whenever a move is goten, do this stuff
            self.cleanup_move(1)

    def do_move(self):
        start, finish = super(CheckersAI, self).do_move()

        row = int(start[1] / 50)
        column = int(start[0] / 50)
        moving = self.board[row][column]
        updateBoard(self.board, row, column, 0)

        row = int(finish[1] / 50)
        column = int(finish[0] / 50)

        # King me
        if (moving == BLACK and row == 0) or (moving == RED and row == 7):
            moving = moving + KING

        updateBoard(self.board, row, column, moving)

        jump = False
        if abs(start[0] - finish[0]) > self.SQUARESIZE:
            jump = True
            row = int((min(start[1], finish[1]) + 50.0) / 50)
            column = int((min(start[0], finish[0]) + 50.0) / 50)
            updateBoard(self.board, row, column, 0)

        if self.moving == 'black':
            next = 1
        else:
            next = 2

        pprint(self.board)

        # Only print jump moves to logs or it'll be too long to print
        if jump:
            with open(self.logfile, 'a') as out:
                pprint(self.board, stream=out)

        total_pieces = 0
        for row in self.board:
            total_pieces += sum([1 for p in row if p != 0])

        #if total_pieces < 8:
        #    #print "pieces %s, changing look ahead value" % total_pieces
        #    self.look_ahead_val = LOOK_AHEAD2
        if total_pieces < 7:
            self.look_ahead_val = LOOK_AHEAD2
        if total_pieces < 4:
            self.look_ahead_val = LOOK_AHEAD3

    def look_ahead(self, board, color):
        depth = self.look_ahead_val - 1
        #self.all_
        moves, m2 = self.find_all_moves(board, color, depth=depth)
        self.expand_nodes(moves, (color % 2) + 1, depth - 1, m2)
        getScores(moves, depth)
        getScores(m2, depth)
        return moves, m2

    def expand_nodes(self, moves, color, depth, moves2):
        score = False
        if depth == 0:
            score = True

        local_best_move_score = None
        for move, cdr in moves.items():
            b = cdr[0]

            cdr2 = moves2[move]

            m, m2 = self.find_all_moves(b, color, score, depth)
            cdr.append(m)
            cdr2.append(m2)
   

            if depth:
                self.expand_nodes(m, (color % 2) + 1, depth-1, m2)
  
                bestScore = getScores(m, depth)
                #cdr[1] = bestScore
                getScores(m2, depth)

            # AB Pruning
                """
            if local_best_move_score == None \
                    or cdr[1] >= local_best_move_score:
                local_best_move_score = cdr[1]
                cdr.append(m)
                cdr2.append(m2)
            else:
                # pruned
                pass
                """


    def find_all_moves(self, board, color, score=False, depth=0):
        all_moves = {}
        m2 = {}
        for i, row in enumerate(board):
            for j, piece in enumerate(row):
                if piece in (color, color + KING):
                    jumps = self.find_jumps(board, i, j, score=score)
                    for b, move, s in jumps:
                        all_moves.setdefault(move, [b, s])
                        m2.setdefault(move, ["bb" + str(depth), s])

        # handle multi-jumps
        if all_moves:
            for mv in all_moves:
                cdr = all_moves[mv]
                multi_jumps = [[cdr[0], mv, cdr[1]]]
                multi_jump_list = []
                while multi_jumps:
                    multi_jumps = self.find_jumps(multi_jumps[0][0],
                                                  multi_jumps[0][1][2],
                                                  multi_jumps[0][1][3],
                                                  score=score)
                    multi_jump_list.extend(multi_jumps)

                for j in multi_jump_list:
                    if all_moves.get(mv):
                        muv = mv + tuple(j[1][2:])
                        cdr[0] = j[0]
                        cdr[1] = j[2]
                        all_moves[muv] = cdr
                        m2[muv] = ['bb' + str(depth), j[2]]
                        del all_moves[mv]
                        del m2[mv]

        if not all_moves:
            for i, row in enumerate(board):
                for j, piece in enumerate(row):
                    if piece in (color, color + KING):
                        moves = self.find_moves(board, i, j, score=score)
                        for b, move, s in moves:
                            all_moves.setdefault(move, [b, s])
                            m2.setdefault(move, ['bb' + str(depth), s])

        return all_moves, m2

    def find_jumps(self, board, i, j, score=False):
        jumps = []
        piece = board[i][j]
        if piece in (RED, RKING):
            jumps.extend(self.check_jump(board, piece, BLACK, i, j, 
                                         i + 1, j - 1, i + 2, j - 2,
                                         score=score))
            jumps.extend(self.check_jump(board, piece, BLACK,  i, j, 
                                         i + 1, j + 1, i + 2, j + 2,
                                         score=score))
            if piece == RKING:
                jumps.extend(self.check_jump(board, piece, BLACK, i, j, 
                                             i - 1, j - 1, i - 2, j - 2,
                                             score=score))
                jumps.extend(self.check_jump(board, piece, BLACK, i, j, 
                                             i - 1, j + 1, i - 2, j + 2,
                                              score=score))
        elif piece in (BLACK, BKING):
            jumps.extend(self.check_jump(board, piece, RED, i, j,
                                         i - 1, j - 1, i - 2, j - 2,
                                         score=score))
            jumps.extend(self.check_jump(board, piece, RED, i, j,
                                         i - 1, j + 1, i - 2, j + 2,
                                         score=score))
            if piece == BKING:
                jumps.extend(self.check_jump(board, piece, RED, i, j,
                                             i + 1, j - 1, i + 2, j - 2,
                                             score=score))
                jumps.extend(self.check_jump(board, piece, RED, i, j,
                                             i + 1, j + 1, i + 2, j + 2,
                                             score=score))

        return jumps

    def check_jump(self, board, piece, jumped_color,
                   si, sj, ji, jj, ei, ej, score=False):
        if -1 < ji < 8 and -1 < jj < 8 and -1 < ei < 8 and -1 < ej < 8:
            if (board[ji][jj] == jumped_color \
                    or board[ji][jj] == jumped_color + KING) \
                    and board[ei][ej] == 0:
                newBoard = copy.deepcopy(board)
                updateBoard(newBoard, si, sj, 0)
                updateBoard(newBoard, ji, jj, 0)
                updateBoard(newBoard, ei, ej, piece)

                s = None
                if score:
                    s = evalBoard(newBoard)

                return [[newBoard, (si, sj, ei, ej), s]]

        return []


    def find_moves(self, board, i, j, score=False):
        moves = []
        piece = board[i][j]
        if piece in (RED, RKING):
            moves.extend(self._check_move(board, piece,
                                          i, j, i + 1, j - 1,
                                          score=score))
            moves.extend(self._check_move(board, piece,
                                          i, j, i + 1, j + 1,
                                          score=score))
            if piece == RKING:
                moves.extend(self._check_move(board, piece,
                                              i, j, i - 1, j - 1,
                                              score=score))
                moves.extend(self._check_move(board, piece,
                                              i, j, i - 1, j + 1,
                                              score=score))
        elif piece in (BLACK, BKING):
            moves.extend(self._check_move(board, piece,
                                          i, j, i - 1, j - 1,
                                          score=score))
            moves.extend(self._check_move(board, piece,
                                          i, j, i - 1, j + 1,
                                          score=score))
            if piece == BKING:
                moves.extend(self._check_move(board, piece,
                                              i, j, i + 1, j - 1,
                                              score=score))
                moves.extend(self._check_move(board, piece,
                                              i, j, i + 1, j + 1,
                                              score=score))

        return moves

    def _check_move(self, board, piece,
                    si, sj, ei, ej, score=False):
        if -1 < ei < 8 and -1 < ej < 8:
            if board[ei][ej] == 0:
                newBoard = copy.deepcopy(board)
                updateBoard(newBoard, si, sj, 0)
                updateBoard(newBoard, ei, ej, piece)

                s = None
                if score:
                    s = evalBoard(newBoard)

                return [[newBoard, (si, sj, ei, ej), s]]

        return []

    def printDebug(self, moves):
        k = moves.keys()[0]
        pprint("depth 0")
        pprint(k)
        pprint(moves[k][0])
        pprint(moves[k][1])
        k2 = moves[k][2].keys()[0]
        pprint("depth 1")
        pprint(k2)
        pprint(moves[k][2][k2][0])
        pprint(moves[k][2][k2][1])
        
        k3 = moves[k][2][k2][2].keys()[0]
        pprint("depth 2")
        pprint(k3)
        pprint(moves[k][2][k2][2][k3][0])
        pprint(moves[k][2][k2][2][k3][1])


def evalBoard(board):
    redScore = 0
    blackScore = 0

    redPieces = 0
    blackPieces = 0
    redPosValue = 0
    blackPosValue = 0

    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece in (RED, RKING):
                posValue = getPositionValue(i, j)
                redScore += ((piece + 1) * 2) + posValue
                redPosValue += posValue
                redPieces += 1
            elif piece in (BLACK, BKING):
                posValue = getPositionValue(i, j)
                blackScore += (piece * 2) + posValue
                blackPosValue += posValue
                blackPieces += 1

    # Ignore positional value at the end of the game
    if redPieces < 4:
        redScore -= redPosValue
        blackScore -= blackPosValue
           
    # game is over if a player has 0 points
    if redScore == 0:
        blackScore = 10000
    if blackScore == 0:
        redScore = 10000

    s = (redScore * -1) + blackScore
    return s

# Note: position value ideas are taken from this article:
# http://ai-depot.com/articles/minimax-explained/3/
def getPositionValue(row, column):
    if row == 0 or row == 7 or column == 0 or column == 7:
        return 3
    elif row == 1 or row == 6 or column == 1 or column == 6:
        return 2
    elif row == 2 or row == 5 or column == 2 or column == 5:
        return 1
    else:
        return 0

def getScores(m, depth):
    bestVal = None
    localBest = None

    min = (LOOK_AHEAD + depth - 1) % 2 == 0

    for _, cdr in m.items():
        if len(cdr) < 3:
            continue
        for _, rest in cdr[2].items():
            if bestVal == None or \
                    (min and rest[1] < bestVal) or \
                    (not min and rest[1] > bestVal):
                bestVal = rest[1]
            if localBest == None or \
                    (min and rest[1] < localBest) or \
                    (not min and rest[1] > localBest):
                localBest = rest[1]
                
        cdr[1] = localBest
        localBest = None
        
    return bestVal

def updateBoard(board, row, column, piece):
    if piece == BLACK and row == 0:
        piece = BKING
    if piece == RED and row == 7:
        piece = RKING
    board[row][column] = piece    

def main(players=1, playerName='Unidentified Player'):
    ai = CheckersAI(players, playerName)
    ai.playGame()

    
if __name__=='__main__':        
    if len(sys.argv) > 1:
        if sys.argv[1] == '2':
            main(2)
        else:
            main(1, sys.argv[1])
    else:
        main()
