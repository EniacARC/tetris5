from board import Board
from piece import Piece
import random

# SHOULD BE OBJECTS
# PIECES = (([(0, 0), (1, 0), (2, 0), (3, 0)], (0, 240, 240)),  # line piece
#           ([(0, 0), (1, 0), (2, 0), (2, 1)], (240, 160, 0)),  # L piece
#           ([(0, 0), (0, 1), (1, 0), (2, 0)], (0, 0, 240),  # reverse L piece
#           [(0, 0), (1, 0), (1, 1), (2, 1)],  # S piece
#           [(0, 1), (1, 0), (1, 1), (2, 0)],  # reverse S piece
#           [(0, 0), (0, 1), (1, 1), (2, 1)],  # [] piece
#           [(0, 0), (1, 0), (1, 1), (2, 0)])  # T piece
PIECES = (Piece([(0, 0), (1, 0), (2, 0), (3, 0)], (0, 240, 240)),  # line piece
          Piece([(0, 0), (1, 0), (2, 0), (2, 1)], (240, 160, 0)),  # L piece
          Piece([(0, 0), (0, 1), (1, 0), (2, 0)], (0, 0, 240)),  # reverse L piece
          Piece([(0, 0), (1, 0), (1, 1), (2, 1)], (0, 240, 0)),  # S piece
          Piece([(0, 1), (1, 0), (1, 1), (2, 0)], (240, 0, 0)),  # reverse S piece
          Piece([(0, 0), (0, 1), (1, 0), (1, 1)], (240, 240, 0)),  # [] piece
          Piece([(0, 0), (1, 0), (1, 1), (2, 0)], (160, 0, 240)))  # T piece

BLACK = (0, 0, 0)

WIDTH = 10
HEIGHT = 20
MIDDLE_POINT = (WIDTH - 1) // 2


class State():

    def __init__(self, board):

        self.game_over = False

        self.board = board
        self.bag = list(PIECES)

        self.current_piece = None

        self.next = random.choice(self.bag)
        # self.bag.remove(self.next)

        self.mask = None
        self.x = 0
        self.y = 0

        # -- move amount a move amount y --
        self.shift_y = -1
        self.shift_x = 0

        self.max_grace = 20
        self.grace_turns = 4
        self.sum_grace = 0
        self.grace = self.grace_turns

    def __set_drop_point(self):
        # find x value for drop
        min_x, max_x = self.current_piece.calculate_x_edge()
        middle_x = (min_x + max_x) // 2
        self.x = MIDDLE_POINT - middle_x

        # find y dropping point:
        min_y, max_y = self.current_piece.calculate_y_edge()
        self.y = HEIGHT - 1 - max_y

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
            if y_value is not None:
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

    def generate_new_piece(self):
        # select a new piece from the bag. if bag is empty create new bag
        # self.bag = list(PIECES) if not self.bag else self.bag
        print()
        for l in self.bag:
            print(l.body)
        print()
        self.current_piece = self.next
        print(self.current_piece.body)
        if len(self.bag) == 1:
            self.bag = list(PIECES)
        else:
            self.bag.remove(self.current_piece)  # we used the piece so remove it from the bag
        self.next = random.choice(self.bag)

        self.mask = Piece(self.current_piece.body, BLACK)
        self.__set_drop_point()
        return self.__check_y_collision()

    def move_x(self):
        if not self.__check_x_collision():
            print(f"moving x to {self.x + self.shift_x}")
            self.__move_piece(self.x + self.shift_x, self.y)

    def move_y(self):
        if not self.__check_y_collision():
            self.__move_piece(self.x, self.y + self.shift_y)
            # print(self.board.widths)
            return False
        else:
            # self.board.update_heights_array()
            # if grace != 0 not pressed
            if self.grace == 0 or self.sum_grace == self.max_grace:
                self.board.lock_piece(self.x, self.y, self.current_piece)
                self.board.clear_rows()
                game_over = self.generate_new_piece()
                self.board.place(self.x, self.y, self.current_piece)

                self.sum_grace = 0
                self.grace = self.grace_turns
                self.game_over = game_over

            self.grace -= 1
            self.sum_grace += 1

    # def __check_pos(self, x, y):
    #     if self.board.can_place(x, y, self.current_piece):
    #         self.__move_piece(self.x, self.y)
    #         self.mask = Piece(self.current_piece.body, BLACK)
    #
    #         self.x, self.y = x, y
    #         return True
    #     else:
    #         return False

    def rotate(self):
        # shift_x, shift_y = self.shift_x, self.shift_y
        # self.shift_x, self.shift_y = 0, 0
        # print("rotating")
        self.current_piece = self.current_piece.rotate_clockwise()
        self.board.place(self.x, self.y, self.mask)
        # if not self.__check_y_collision() and not self.__check_y_collision():
        invalid_move = True
        for dx, dy in [(0, 0), (0, 1), (1, 0), (-1, 0)]:
            if self.board.can_place(self.x + dx, self.y + dy, self.current_piece):
                self.__move_piece(self.x + dx, self.y + dy)
                self.mask = Piece(self.current_piece.body, BLACK)
                invalid_move = False
                break

        if invalid_move:
            print("invalid")
            self.current_piece = self.current_piece.rotate_counter_clockwise()
            self.board.place(self.x, self.y, self.current_piece)

