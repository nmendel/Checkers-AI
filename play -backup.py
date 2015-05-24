
import sys
import random
import copy
from pprint import pprint

import checkers

# TODO: 
#  Support multi-jumps
#  Min-max
#  AB Pruning

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
LOOK_AHEAD = 3
MIN = False
MAX = True

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

    cur_move = None
    best_move = None
    best_move_score = None

    def __init__(self, numPlayers=1):
        checkers.CheckersInterface.__init__(self)
        self.board = self.START_BOARD
        #self.ci = checkers.CheckersInterface(self.START_BOARD)
        self.boardSize = self.SQUARESIZE * 8
        if numPlayers == 2:
            self.aiPlaying = False;

    def playGame(self):
        self.setup_move()

        while not self.GameDone():
            if self.end_now:
                break

            if self.moving == 'black' and self.aiPlaying:
                # self.try_random_moves()
                self.ai_move()

            self.MoveLoop()

        self.endGame()
        

    def try_random_moves(self):
        self.got_piece = 0
        self.got_move = 0

        print "trying to move"
        while not self.got_piece:
            x = random.randint(0, self.boardSize)
            y = random.randint(0, self.boardSize)
            self.get_piece_click(event(x, y))

        print "got a piece"

        while not self.got_move:
            x = random.randint(0, self.boardSize)
            y = random.randint(0, self.boardSize)
            self.get_square_click(event(x, y))
        
        print "moving"

    def ai_move(self):
        moves, m2 = self.look_ahead(self.board, BLACK)

        pprint(self.board)
        print "All valid moves for %s:" % BLACK

        pprint(moves.values()[0][2].values()[0][2])

        pprint("Best move: %s, score: %s"
               % (self.best_move, self.best_move_score))
        
        print "moves.values()[1][2].values()[1][1]"
        print moves.values()[1][2].values()[1][1]
        print moves.values()[1][1]

        # printScores(moves)

        move = moves.keys()[0]
        import pdb
        pdb.set_trace()

        self.get_piece_click(event(move[1] * self.SQUARESIZE + EXTRA,
                                   move[0] * self.SQUARESIZE + EXTRA))
        self.get_square_click(event(move[3] * self.SQUARESIZE + EXTRA,
                                    move[2] * self.SQUARESIZE + EXTRA))


    def MoveLoop(self):
        self.master.update()
        if self.got_move:
            if not self.check_move():
                    #whenever a move is gotten which is correct, do this stuff
                self.do_move()
                self.cleanup_move(2)
                self.setup_move()
                self.cleanup_move(3)
            # whenever a move is goten, do this stuff
            self.cleanup_move(1)

    def do_move(self):
        start, finish = super(CheckersAI, self).do_move()
        pprint("Start: %s, Finish: %s" % (start, finish))
        self.updateBoard(start, 0)
        self.updateBoard(finish, 1)

        if abs(start[0] - finish[0]) > self.SQUARESIZE:
            print "JMMMMPPPED"
            self.updateBoard([min(start[0], finish[0]) + 50.0, 
                              min(start[1], finish[1]) + 50.0], 0)


        if self.moving == 'black':
            next = 1
        else:
            next = 2

        self.cur_move = None
        self.best_move = None
        self.best_move_score = None


    def updateBoard(self, coords, piece):
        print "update board : %s, %s" % (coords, piece)

        if piece and self.moving == 'black':
            piece = 2

        row = int(coords[1] / 50)
        column = int(coords[0] / 50)
        updateBoard(self.board, row, column, piece)

    def look_ahead(self, board, color):
        depth = LOOK_AHEAD - 1
        moves, m2 = self.find_all_moves(board, color)
        self.expand_nodes(moves, (color % 2) + 1, depth - 1, MIN, m2)
        self.set_scores(moves)
        return moves, m2

    def set_scores(self, moves):
        for vals in moves.values():
            if len(vals) == 3:
                vals[1] = getScores2(vals[2], BLACK)

        return getScores2(moves, BLACK)
                

    def expand_nodes(self, moves, color, depth, minmax, m2):
        score = False
        if depth == 0:
            score = True

        # TODO: loop through m2 instead of or in addition to moves
        for move, cdr in moves.items():
            if depth == LOOK_AHEAD - 1:
                self.cur_move = move

            b = cdr[0]

            m, m2 = self.find_all_moves(b, color, score)
            cdr.append(m)

            if depth:
                cdr[1] = self.expand_nodes(m, (color % 2) + 1,
                                           depth-1, not minmax, m2)
    
                cdr[1] = getScores(m, minmax)

    def find_all_moves(self, board, color, score=False):
        all_moves = {}
        m2 = {}
        for i, row in enumerate(board):
            for j, piece in enumerate(row):
                if piece in (color, color + KING):
                    jumps = self.find_jumps(board, i, j, score=score)
                    for b, move, s in jumps:
                        all_moves.setdefault(move, [b, s])
                        m2.setdefault(move, ["bb", s])

        if not all_moves:
            for i, row in enumerate(board):
                for j, piece in enumerate(row):
                    if piece in (color, color + KING):
                        moves = self.find_moves(board, i, j, score=score)
                        for b, move, s in moves:
                            all_moves.setdefault(move, [b, s])
                            m2.setdefault(move, ['bb', s])

        return all_moves, m2

    def find_jumps(self, board, i, j, score=False, multi=""):
        jumps = []
        piece = board[i][j]
        if piece in (RED, RKING) or multi in (RED, RKING):
            jumps.extend(self.check_jump(board, piece, BLACK, i, j, 
                                         i + 1, j - 1, i + 2, j - 2,
                                         score=score))
            jumps.extend(self.check_jump(board, piece, BLACK,  i, j, 
                                         i + 1, j + 1, i + 2, j + 2,
                                         score=score))
            if piece == RKING or multi == RKING:
                jumps.extend(self.check_jump(board, piece, BLACK, i, j, 
                                             i - 1, j - 1, i - 2, j - 2,
                                             score=score))
                jumps.extend(self.check_jump(board, piece, BLACK, i, j, 
                                             i - 1, j + 1, i - 2, j + 2,
                                              score=score))
        elif piece in (BLACK, BKING) or multi in (BLACK, BKING):
            jumps.extend(self.check_jump(board, piece, RED, i, j,
                                         i - 1, j - 1, i - 2, j - 2,
                                         score=score))
            jumps.extend(self.check_jump(board, piece, RED, i, j,
                                         i - 1, j + 1, i - 2, j + 2,
                                         score=score))
            if piece == RKING or multi == RKING:
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
                    s = self.evalBoard(newBoard)

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
            if piece == RKING:
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
                    s = self.evalBoard(newBoard)

                return [[newBoard, (si, sj, ei, ej), s]]

        return []

    def evalBoard(self, board):
        redScore = 0
        blackScore = 0

        for i, row in enumerate(board):
            for j, piece in enumerate(row):
                if piece in (RED, RKING):
                    redScore += piece + 1
                elif piece in (BLACK, BKING):
                    blackScore += piece

        s = (blackScore * -1) + redScore

        if self.best_move_score == None or s > self.best_move_score:
            self.best_move_score = s
            self.best_move = self.cur_move

        return s

def getScores2(m, minmax):
    bestVal = None

    for _, rest in m.items():
        if bestVal == None or \
                (minmax == MIN and rest[1] < bestVal) or \
                (minmax == MAX and rest[1] > bestVal):
            bestVal = rest[1]
        
    return bestVal

def getScores(m, minmax):
    bestVal = None

    for _, (_, _, mvs) in m.items():
        for _, rest in mvs.items():
            if bestVal == None or \
                    (minmax == MIN and rest[1] < bestVal) or \
                    (minmax == MAX and rest[1] > bestVal):
                bestVal = rest[1]
        
    return bestVal

def printScores(m):
    val = ""
    for _, cdr in m.items():
        val += str(cdr[1]) + " "
        if len(cdr) == 3:
            printScores(cdr[2])

    print val

def updateBoard(board, row, column, piece):
    board[row][column] = piece    

def main(players=1):
    ai = CheckersAI(players)
    ai.playGame()

    
if __name__=='__main__':        
    if len(sys.argv) > 1 and sys.argv[1] == '2':
        main(2)
    else:
        main()
