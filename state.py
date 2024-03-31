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

    # def __check_for_collision(self, shift_x, shift_y):
    #     #
    #     # min_x, max_x = self.current_piece.calculate_x_edge()
    #     #
    #     # if min_x + self.x == 0 or self.x + max_x == WIDTH - 1:
    #     #     return True
    #     #
    #     # skirt = self.current_piece.skirt()
    #     # for i, y in enumerate(skirt):
    #     #
    #     #     if self.y + y == 0 or self.board.board[self.y + y + shift_y][self.x + i + shift_x] != BLACK:
    #     #         return True
    #     # return False
    #     print(f"{self.x}, {self.y}")
    #     min_x, max_x = self.current_piece.calculate_x_edge()
    #     new_min_x = self.x + min_x + shift_x
    #     new_max_x = self.x + max_x + shift_x
    #
    #     if new_min_x < 0 or new_max_x >= WIDTH:
    #         return True, False
    #
    #
    #     for i, y in enumerate(skirt):
    #         new_y = self.y + y + shift_y
    #         if new_y < 0:
    #             return True, True
    #         # for x in range(min_x, max_x + 1):
    #         #     new_x = self.x + x + shift_x
    #         #     print(f"testing: {new_x}, {new_y}:", end=" ")
    #         #     print(f"value: {self.board.board[new_y][new_x]}")
    #         #     if self.board.board[new_y][new_x] != BLACK:
    #         #         return True, True
    #
    #     return False, False

    # def __down_col(self):
    #     move_down = True
    #     skirt = [i + self.shift_y for i in self.current_piece.skirt()]
    #     # if min(skirt) + self.y <= 0:
    #     #     self.y = 0
    #     #     move_down = False
    #
    #     # uses the heights array to check for collisions
    #     for i, y, in enumerate(skirt):
    #         print(f"checking: y: {self.y + y}")
    #         if not move_down:
    #             break
    #         if self.y + y - self.board.heights[i + self.x] < 1:
    #             move_down = False
    #             self.y = self.board.heights[i + self.x]
    #     return move_down
    #
    # def __side_col(self):
    #     min_cells, max_cells = self.current_piece.belt()
    #     for i, x in enumerate(min_cells):
    #         print(f"checking: min x: {self.x + x + self.shift_x}")
    #         if self.x + x + self.shift_x < 0 or self.x + max_cells[i] + self.shift_x >= WIDTH:
    #             return True
    #         for j, y in enumerate(self.current_piece.body):
    #             if self.board.board[self.y + y[1]][self.x + x + self.shift_x + j] != BLACK:
    #                 return True
    #     return False

    # def move_piece(self):
    #     print(f"{self.x}, {self.y}")
    #     new_y, new_x = self.y, self.x
    #     if not self.__down_col():
    #         new_y += self.shift_y
    #     if not self.__side_col():
    #         new_x += self.shift_x
    #
    #
    #
    #     self.board.place(self.x, self.y, self.mask)
    #     self.x = new_x
    #     self.y = new_y
    #     self.board.place(self.x, self.y, self.current_piece)
    #
    #     if not self.__down_col():
    #         self.generate_new_piece()
    #         self.board.place(self.x, self.y, self.current_piece)

    def __check_collision(self):

        # check for edges
        for point in self.current_piece.body:
            x = point[0] + self.x + self.shift_x
            if x < 0 or x > WIDTH - 1:
                self.shift_x = 0
                break

        skirt = self.current_piece.skirt()
        print(skirt)
        for i, y_value in enumerate(skirt):
            y = y_value + self.y + self.shift_y
            print(f"{y} : {self.board.heights[i + self.x]}")
            if y < 0 or y + self.shift_y < self.board.heights[i + self.x]:
                self.shift_y = 0
        # for point in self.current_piece.body:
        #     y = point[1] + self.y + self.shift_y
        #     print(point[1], self.y, self.shift_y)
        #     print(f"my y: {y - self.shift_y}. heights at {x} is: {self.board.heights[x]}")
        #     if y < 0:  # CHECK WITH HEIGHTS ARRAY
        #         self.shift_y = 0

        print(f"passed: {self.shift_y}")
        x_const, y_const = self.x + self.shift_x, self.y + self.shift_y

        # check for overlap
        for point in self.current_piece.body:
            x = point[0] + x_const
            y = point[1] + y_const
            # print(f"{x}, {y}")
            if self.board.board[y][x] != BLACK and (point[0] + self.shift_x, point[1] + self.shift_y) not in self.current_piece.body:
                print(x, y)
                return True

        # print("valid")
        return False

    def move_piece(self):
        if not self.__check_collision():
            self.board.place(self.x, self.y, self.mask)
            self.x += self.shift_x
            self.y += self.shift_y
            self.board.place(self.x, self.y, self.current_piece)

            # If there's a downward collision, generate a new piece
        if self.shift_y == 0:
            # we place the piece
            self.board.update_heights_array()
            self.shift_y = -1
            self.generate_new_piece()
            self.board.place(self.x, self.y, self.current_piece)


