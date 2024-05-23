from board import Board
from piece import Piece
import random

# define all the pieces
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


class State:
    """
        A class representing the current state of the Tetris game.

        Attributes:
            game_over (bool): Indicates whether the game is over.
            board (Board): The game board.
            bag (list): A list of remaining pieces to be used.
            current_piece (Piece): The currently active piece.
            next (Piece): The next piece to be used.
            mask (Piece): A temporary piece used for visualizing the current piece's movement.
            x (int): The x-coordinate of the current piece.
            y (int): The y-coordinate of the current piece.
            shift_y (int): The amount to shift the piece vertically.
            shift_x (int): The amount to shift the piece horizontally.
            max_grace (int): The maximum number of grace turns.
            grace_turns (int): The number of grace turns.
            sum_grace (int): The sum of grace turns.
            grace (int): The current number of grace turns.
        """

    def __init__(self, board):
        """
        Initialize a new State object with a given board.

        :param board: The game board.
        :type board: Board

        :return: None
        """
        # the game isn't over so game_over is false
        self.game_over = False

        # define the board the list of pieces
        self.board = board
        self.bag = list(PIECES)

        # define the next piece and current piece
        self.current_piece = None
        self.next = random.choice(self.bag)

        # define piece mask and coordinates
        self.mask = None
        self.x = 0
        self.y = 0

        # define the way the piece would shift in the first turn
        self.shift_y = -1
        self.shift_x = 0

        # define grace constants
        self.max_grace = 20
        self.grace_turns = 4
        self.sum_grace = 0
        self.grace = self.grace_turns

    def __set_drop_point(self):
        """
        Set the drop point for the current piece.

        :return: None
        """
        # find x value for drop
        min_x, max_x = self.current_piece.calculate_x_edge()
        middle_x = (min_x + max_x) // 2
        self.x = MIDDLE_POINT - middle_x

        # find y dropping point:
        min_y, max_y = self.current_piece.calculate_y_edge()
        self.y = HEIGHT - 1 - max_y

    def __move_piece(self, new_x, new_y):
        """
        Move the current piece to a new position.

        :param new_x: The new x-coordinate of the piece.
        :type new_x: int
        :param new_y: The new y-coordinate of the piece.
        :type new_y: int

        :return: None
        """
        self.board.place(self.x, self.y, self.mask)
        self.x = new_x
        self.y = new_y
        self.board.place(self.x, self.y, self.current_piece)

    def __check_x_collision(self):
        """
        Check for collisions in the x-direction for the current piece.

        :return: True if there is a collision, False otherwise.
        :rtype: bool
        """
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
        """
        Check for collisions in the y-direction for the current piece.

        :return: True if there is a collision, False otherwise.
        :rtype: bool
        """
        skirt = self.current_piece.skirt()
        for i, y_value in enumerate(skirt):
            if y_value is not None:
                y = y_value + self.y + self.shift_y
                if y < 0:
                    return True

        for point in self.current_piece.body:
            x = point[0] + self.x
            y = point[1] + self.y + self.shift_y
            if self.board.board[y][x] != BLACK and (point[0], point[1] + self.shift_y) not in self.current_piece.body:
                return True

        return False

    def generate_new_piece(self):
        """
        Generate a new piece and check for game over.

        :return: True if the game is over, False otherwise.
        :rtype: bool
        """
        self.current_piece = self.next
        if len(self.bag) == 1:
            self.bag = list(PIECES)
        else:
            self.bag.remove(self.current_piece)  # we used the piece so remove it from the bag
        self.next = random.choice(self.bag)

        self.mask = Piece(self.current_piece.body, BLACK)
        self.__set_drop_point()
        return self.__check_y_collision()

    def move_x(self):
        """
        Move the current piece horizontally.

        :return: None
        """
        if not self.__check_x_collision():
            self.__move_piece(self.x + self.shift_x, self.y)

    def move_y(self):
        """
        Move the current piece vertically.

        :return: True if the piece cannot move further down, False otherwise.
        :rtype: bool
        """
        if not self.__check_y_collision():
            self.__move_piece(self.x, self.y + self.shift_y)
            return False

        else:
            if self.grace == 0 or self.sum_grace == self.max_grace:
                self.board.update_widths()
                self.board.clear_rows()

                game_over = self.generate_new_piece()
                self.board.place(self.x, self.y, self.current_piece)

                self.sum_grace = 0
                self.grace = self.grace_turns
                self.game_over = game_over

            self.grace -= 1
            self.sum_grace += 1

    def rotate(self):
        """
        Rotate the current piece clockwise.

        :return: None
        """
        self.current_piece = self.current_piece.rotate_clockwise()
        self.board.place(self.x, self.y, self.mask)

        invalid_move = True
        for dx, dy in [(0, 0), (0, 1), (1, 0), (-1, 0)]:
            if self.board.can_place(self.x + dx, self.y + dy, self.current_piece):
                self.__move_piece(self.x + dx, self.y + dy)
                self.mask = Piece(self.current_piece.body, BLACK)
                invalid_move = False
                break
        if invalid_move:
            self.current_piece = self.current_piece.rotate_counter_clockwise()
            self.board.place(self.x, self.y, self.current_piece)

    def add_lines(self, num_of_lines):
        """
        Add new lines to the board.

        :param num_of_lines: The number of lines to add.
        :type num_of_lines: int

        :return: None
        """
        self.board.place(self.x, self.y, self.mask)
        self.board.add_rows(num_of_lines)
        self.board.place(self.x, self.y, self.current_piece)
        self.board.update_widths()