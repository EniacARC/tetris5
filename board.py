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
            if self.board[y + point[1]][x + point[0]] != 0:
                return "BAD"

        for point in piece.body:
            self.board[y + point[1]][x + point[0]] = piece.color

            # update the widths and heights arrays to reflect the added piece

            self.widths[y + point[1]] += 1
            self.heights[x + point[0]] = max(self.heights[x + point[0]], y + point[1])
        self.current_piece = piece
        return "PLC"

    def __clear_line(self, line_num):
        self.board[line_num] = [0] * WIDTH
        self.widths[line_num] = 0  # new line has no pieces

    # -----------------WORKS?-----------------
    # !!!!!!!!!!!!!!!HEIGHTS ARRAY DOESN'T UPDATE!!!!!!!!!!!!!!!
    def __move_down(self, rows_move_down):
        for i, move_amount in enumerate(rows_move_down):
            if move_amount > 0:
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

    # def draw(self, screen): for i in range(BOARD_HEIGHT): for j in range(BOARD_WIDTH): if self.grid[i][j] != 0:
    # pygame.draw.rect(screen, self.grid[i][j], (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
