import random

import pygame
from piece import Piece

WIDTH = 10
HEIGHT = 20

BLACK = (0, 0, 0)
GRAY = (105, 105, 105)


class Board():

    def __init__(self):
        # self.colors = {1: (255, 255, 255)}  # converts piece type (1, 2, 3, etc.) to color
        self.board = [[BLACK for i in range(WIDTH)] for j in range(HEIGHT)]  # (0, 0, 0) means empty
        self.widths = [0 for i in range(HEIGHT)]
        # self.heights = [-1 for i in range(WIDTH)]
        # self.current_piece = None  # ~redundant maybe~
        self.cleared = 0

    def can_place(self, x, y, piece):
        for point in piece.body:
            if x + point[0] >= WIDTH or x + point[0] < 0 or y + point[1] >= HEIGHT or y + point[1] < 0:
                return False
            # self.board.board[y][x] != BLACK and (point[0], point[1] + self.shift_y) not in self.current_piece.body
            if self.board[y + point[1]][x + point[0]] != BLACK:
                return False
        return True

    def place(self, x, y, piece):
        for point in piece.body:
            self.board[y + point[1]][x + point[0]] = piece.color

    def update_widths(self):
        for i, row in enumerate(self.board):
            self.widths[i] = sum(1 for elem in row if elem != BLACK)

    def lock_piece(self, x, y, piece):
        # print(y)
        for point in piece.body:
            # print(point[0], point[1])
            self.widths[y + point[1]] += 1
            # self.heights[x + point[0]] = max(self.heights[x + point[0]], y + point[1])

    def __clear_line(self, line_num):
        self.board[line_num] = [BLACK] * WIDTH  # clear line
        self.widths[line_num] = 0  # new line has no pieces

    # -----------------WORKS?-----------------
    def __move_down(self, rows_move_down):
        max_move_amount = 0
        for i, move_amount in enumerate(rows_move_down):
            if move_amount > 0:
                max_move_amount = max(0, move_amount)
                target_row = i - move_amount
                if target_row >= 0:
                    self.board[target_row] = self.board[i]
                    self.widths[target_row] = self.widths[i]
                    self.__clear_line(i)

    def clear_rows(self):
        rows_move_down = [0 for i in range(HEIGHT)]  # 0 index is the first row
        down = 0

        # 0 = don't move down, num > 0 = move down line num lines
        for i in range(HEIGHT):
            if self.widths[i] == WIDTH:
                down += 1
                rows_move_down[i] = 0
                # clear the row
                # temp_board = self.__clear_line(temp_board, HEIGHT - 1 - i)
                self.__clear_line(i)
            else:
                rows_move_down[i] = down

        self.__move_down(rows_move_down)
        self.cleared += down
        return down  # numbers of new lines cleared

    def add_row(self, num_of_rows):
        rand_col = random.randint(0, len(self.board[0]) - 1)
        for i in range(num_of_rows):
            # move rows 1 row down
            for j in range(len(self.board) - 1, 0, -1):
                self.board[j] = self.board[j - 1]
                self.widths[j] = self.widths[j - 1]
            self.board[0] = [GRAY] * len(self.board[0])
            self.board[0][rand_col] = BLACK
