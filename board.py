import pygame
from piece import Piece

WIDTH = 10
HEIGHT = 20

BLACK = (0, 0, 0)

class Board():

    def __init__(self):
        # self.colors = {1: (255, 255, 255)}  # converts piece type (1, 2, 3, etc.) to color
        self.board = [[BLACK for i in range(WIDTH)] for j in range(HEIGHT)]  # (0, 0, 0) means empty
        self.widths = [0 for i in range(HEIGHT)]
        self.heights = [-1 for i in range(WIDTH)]
        # self.current_piece = None  # ~redundant maybe~
        self.cleared = 0

    def can_place(self, x, y, piece):
        for point in piece.body:
            if x + point[0] >= WIDTH or x + point[0] < 0 or y + point[1] >= HEIGHT or y + point[1] < 0:
                return False
            if self.board[y + point[1]][x + point[0]] != BLACK:
                return False
        return True

    def place(self, x, y, piece):
        for point in piece.body:
            self.board[y + point[1]][x + point[0]] = piece.color

            # update the widths array the added piece

            self.widths[y + point[1]] += 1
            # self.heights[x + point[0]] = max(self.heights[x + point[0]], y + point[1])
        # self.current_piece = piece
        # return "PLC"

    def __clear_line(self, line_num):
        self.board[line_num] = [BLACK] * WIDTH # clear line
        self.widths[line_num] = 0  # new line has no pieces

    # -----------------WORKS?-----------------
    # FIXED: !!!!!!!!!!!!!!!HEIGHTS ARRAY DOESN'T UPDATE!!!!!!!!!!!!!!!
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

        for i in range(len(self.heights)):
            self.heights[i] = max(0, self.heights[i] - max_move_amount + 1)

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

    def update_heights_array(self):
        # should be called upon when a piece is set
        self.heights = [-1 for i in range(WIDTH)]

        for j in range(WIDTH):
            for i in range(HEIGHT - 1, -1, -1):
                if self.board[i][j] != BLACK:
                    self.heights[j] = i
                    break

        print(self.heights)

    # def draw(self, screen): for i in range(BOARD_HEIGHT): for j in range(BOARD_WIDTH): if self.grid[i][j] != 0:
    # pygame.draw.rect(screen, self.grid[i][j], (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
