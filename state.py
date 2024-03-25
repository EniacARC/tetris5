from board import Board
from piece import Piece
import random

#SHOULD BE OBJECTS
PIECES = ([(1, 0), (1, 1), (1, 2)],  # line piece
          [(0, 0), (0, 1), (0, 2), (1, 0)],  # L piece
          [(1, 0), (2, 0), (2, 1), (2, 2)],  # reverse L piece
          [(0, 0), (1, 0), (1, 1), (2, 1)],  # S piece
          [(0, 1), (1, 0), (1, 1), (2, 0)],  # reverse S piece
          [(0, 0), (0, 1), (1, 1), (2, 1)],  # [] piece
          [(0, 0), (1, 0), (1, 1), (2, 0)])  # T piece

BLACK = (0, 0, 0)

WIDTH = 10
HEIGHT = 20
MIDDLE_POINT = (WIDTH - 1) // 2


class State():

    def __init__(self, board):
        self.board = board
        self.bag = list(PIECES)
        self.current_piece = None
        self.mask = None
        self.x = 0
        self.y = 0

    def __set_drop_point(self):
        # find x value for drop
        min_x, max_x = self.current_piece.calculate_x_edge()
        middle_x = (min_x + max_x) // 2
        self.x = MIDDLE_POINT - middle_x

        #find y dropping point:
        min_y, max_y = self.current_piece.calculate_y_edge()
        self.y = HEIGHT - 1 - max_y
    def generate_new_piece(self):

        #select a new piece from the bag. if bag is empty create new bag
        self.bag = list(PIECES) if self.bag is None else self.bag
        self.current_piece = random.choice(self.bag)
        self.mask = Piece(self.current_piece.body, BLACK)
        self.bag.remove(self.current_piece) # we used the piece so remove it from the bag
        self.__set_drop_point()


    # def move_piece_down(self):

