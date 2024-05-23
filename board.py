import random

import pygame
from piece import Piece

WIDTH = 10
HEIGHT = 20

BLACK = 0
GRAY = 1


class Board:
    """
    A class representing the game board in Tetris.

    Attributes:
        board (list): A 2D list representing the colors of the cells on the board.
        widths (list): A list representing the number of filled cells in each row.
        cleared (int): The total number of cleared lines.
    """
    def __init__(self):
        """
        Initialize a new Board object.

        :return: None
        """
        self.board = [[BLACK for i in range(WIDTH)] for j in range(HEIGHT)]  # (0, 0, 0) means empty
        self.widths = [0 for i in range(HEIGHT)]
        self.cleared = 0

    def can_place(self, x, y, piece):
        """
        Check if a piece can be placed at a given position on the board.

        :param x: The x-coordinate of the top-left corner of the piece.
        :type x: int
        :param y: The y-coordinate of the top-left corner of the piece.
        :type y: int
        :param piece: The piece to be placed.
        :type piece: Piece

        :return: True if the piece can be placed, False otherwise.
        :rtype: bool
        """
        for point in piece.body:
            if x + point[0] >= WIDTH or x + point[0] < 0 or y + point[1] >= HEIGHT or y + point[1] < 0:
                return False

            if self.board[y + point[1]][x + point[0]] != BLACK:
                return False
        return True

    def place(self, x, y, piece):
        """
        Place a piece on the board at a given position.

        :param x: The x-coordinate of the top-left corner of the piece.
        :type x: int
        :param y: The y-coordinate of the top-left corner of the piece.
        :type y: int
        :param piece: The piece to be placed.
        :type piece: Piece

        :return: None
        """
        for point in piece.body:
            self.board[y + point[1]][x + point[0]] = piece.color

    def update_widths(self):
        """
        Update the number of filled cells in each row of the board.

        :return: None
        """
        for i, row in enumerate(self.board):
            self.widths[i] = sum(1 for elem in row if elem != BLACK)

    def lock_piece(self, x, y, piece):
        """
        Lock a piece on the board at a given position.

        :param x: The x-coordinate of the top-left corner of the piece.
        :type x: int
        :param y: The y-coordinate of the top-left corner of the piece.
        :type y: int
        :param piece: The piece to be locked.
        :type piece: Piece

        :return: None
        """
        for point in piece.body:
            self.widths[y + point[1]] += 1

    def __clear_line(self, line_num):
        """
        Clear a line on the board.

        :param line_num: The index of the line to be cleared.
        :type line_num: int

        :return: None
        """
        self.board[line_num] = [BLACK] * WIDTH  # clear line
        self.widths[line_num] = 0  # new line has no pieces

    def __move_down(self, rows_move_down):
        """
        Move rows down according to the given list.

        :param rows_move_down: A list specifying the number of rows to move down for each row.
        :type rows_move_down: list

        :return: None
        """
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
        """
        Clear filled rows on the board.

        :return: The number of cleared rows.
        :rtype: int
        """
        rows_move_down = [0 for i in range(HEIGHT)]  # 0 index is the first row
        down = 0

        # 0 = don't move down, num > 0 = move down line num lines
        for i in range(HEIGHT):
            if self.widths[i] == WIDTH:
                down += 1
                rows_move_down[i] = 0
                self.__clear_line(i)
            else:
                rows_move_down[i] = down

        self.__move_down(rows_move_down)
        self.cleared += down
        return down  # numbers of new lines cleared

    def add_rows(self, num_of_rows):
        """
        Add new rows to the top of the board.

        :param num_of_rows: The number of rows to add.
        :type num_of_rows: int

        :return: None
        """
        rand_col = random.randint(0, len(self.board[0]) - 1)
        for i in range(num_of_rows):
            # move rows 1 row down
            for j in range(len(self.board) - 1, 0, -1):
                self.board[j] = self.board[j - 1]
                self.widths[j] = self.widths[j - 1]

            self.board[0] = [GRAY] * len(self.board[0])
            self.board[0][rand_col] = BLACK