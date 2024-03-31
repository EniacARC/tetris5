from board import Board
from piece import Piece
import random

# SHOULD BE OBJECTS
# PIECES = ([(1, 0), (1, 1), (1, 2)],  # line piece
#           [(0, 0), (0, 1), (0, 2), (1, 0)],  # L piece
#           [(1, 0), (2, 0), (2, 1), (2, 2)],  # reverse L piece
#           [(0, 0), (1, 0), (1, 1), (2, 1)],  # S piece
#           [(0, 1), (1, 0), (1, 1), (2, 0)],  # reverse S piece
#           [(0, 0), (0, 1), (1, 1), (2, 1)],  # [] piece
#           [(0, 0), (1, 0), (1, 1), (2, 0)])  # T piece
PIECES = (Piece([(0, 0), (1, 0), (1, 1), (2, 1)], (255, 0, 0)),
          Piece([(0, 0), (0, 1), (0, 2), (1, 0)], (0, 0, 255)))

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

        # -- move amount a move amount y --
        self.shift_y = -1
        self.shift_x = 0

    def __set_drop_point(self):
        # find x value for drop
        min_x, max_x = self.current_piece.calculate_x_edge()
        middle_x = (min_x + max_x) // 2
        self.x = MIDDLE_POINT - middle_x

        # find y dropping point:
        min_y, max_y = self.current_piece.calculate_y_edge()
        self.y = HEIGHT - 1 - max_y

    def generate_new_piece(self):
        # select a new piece from the bag. if bag is empty create new bag
        self.bag = list(PIECES) if not self.bag else self.bag
        self.current_piece = random.choice(self.bag)
        self.mask = Piece(self.current_piece.body, BLACK)
        self.bag.remove(self.current_piece)  # we used the piece so remove it from the bag
        self.__set_drop_point()

    def __move_piece(self, new_x, new_y):
        self.board.place(self.x, self.y, self.mask)
        self.x = new_x
        self.y = new_y
        self.board.place(self.x, self.y, self.current_piece)

    def __check_x_collision(self):
        # check for edges
        for point in self.current_piece.body:
            x = point[0] + self.x + self.shift_x
            y = point[1] + self.y

            if x < 0 or x > WIDTH - 1:
                return True

            if self.board.board[y][x] != BLACK and (point[0] + self.shift_x, point[1]) not in self.current_piece.body:
                return True

        return False

    def __check_y_collision(self):
        skirt = self.current_piece.skirt()
        # print(skirt)
        for i, y_value in enumerate(skirt):
            y = y_value + self.y + self.shift_y
            # print(f"{y} : {self.board.heights[i + self.x + self.shift_x]}")
            # or y + self.shift_y < self.board.heights[self.x]:
            if y < 0:
                return True
        for point in self.current_piece.body:
            x = point[0] + self.x
            y = point[1] + self.y + self.shift_y
            if self.board.board[y][x] != BLACK and (point[0], point[1] + self.shift_y) not in self.current_piece.body:
                return True

        return False

    def move_x(self):
        if not self.__check_x_collision():
            print(f"moving x to {self.x + self.shift_x}")
            self.__move_piece(self.x + self.shift_x, self.y)

    def move_y(self):
        if not self.__check_y_collision():
            self.__move_piece(self.x, self.y + self.shift_y)
        else:
            self.board.update_heights_array()
            self.generate_new_piece()
            self.board.place(self.x, self.y, self.current_piece)
