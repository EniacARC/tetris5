import pygame
from piece import Piece

WIDTH = 10
HEIGHT = 20


class Board():

    def __init__(self):
        self.colors = {1: (255, 255, 255)}  # converts piece type (1, 2, 3, etc.) to color
        self.board = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]  # 0 means empty
        self.widths = [0 for i in range(HEIGHT)]
        self.heights = [0 for i in range(WIDTH)]
        self.current_piece = None  # ~redundant maybe~
        self.cleared = 0

    def place(self, x, y, piece):
        for point in piece.body:
            if x + point[0] >= WIDTH or x + point[0] < 0 or y + point[1] >= HEIGHT or y + point[1] < 0:
                "OOB"
            if self.board[x + point[0]][y + point[1]] != 0:
                return "BAD"

        for point in piece.body:
            self.board[x + point[0]][y + point[1]] = piece.color

            # update the widths and heights arrays to reflect the added piece

            self.widths[HEIGHT - y + point[1] - 1] += 1
            self.heights[WIDTH - x + point[0] - 1] += 1
        self.current_piece = piece
        return "PLC"

    def __clear_line(self, line_num):
        self.board[line_num] = [0] * WIDTH
        self.widths[line_num] = 0  # new line has no pieces

    # -----------------WORKS?-----------------
    def __move_down(self, rows_move_down):
        for i, move_amount in enumerate(rows_move_down):
            if move_amount > 0:
                target_row = i - move_amount
                if target_row >= 0:
                    self.board[target_row] = self.board[i]
                    self.__clear_line(i)

    def clear_rows(self):
        rows_move_down = [0 for i in range(HEIGHT)]  # 0 index is the first row
        down = 1 if self.widths[HEIGHT - 1] == WIDTH else 0

        # 0 = don't move down, num > 0 = move down line num lines
        for i in range(1, HEIGHT):
            if self.widths[HEIGHT - 1 - i] == WIDTH:
                down += 1
                rows_move_down[HEIGHT - 1 - i] = 0
                # clear the row
                # temp_board = self.__clear_line(temp_board, HEIGHT - 1 - i)
                self.__clear_line(HEIGHT - 1 - i)
            else:
                rows_move_down[HEIGHT - 1 - i] = down

        self.__move_down(rows_move_down)
        return down  # numbers of new lines cleared
