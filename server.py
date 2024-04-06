# Import your classes
import pickle
import time
import socket
import pygame
from board import Board
from piece import Piece
from state import State

# Constants
BLOCK_SIZE = 24
MINI_BLOCK = 24 // 2
WIDTH = 10  # Number of columns
HEIGHT = 20  # Number of rows
WINDOW_SIZE = (1008, 1008)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

MY_IP = "127.0.0.1"
MY_PORT = 7372
BUFFER_SIZE = 2048


def draw_grid(screen, board, size, start_x, start_y):
    for y, row in enumerate(board.board):
        for x, cell in enumerate(row):
            color = cell
            rect = pygame.Rect((start_x + x) * size, (HEIGHT - start_y - y - 1) * size, size, size)
            pygame.draw.rect(screen, GRAY, rect, 1)
            pygame.draw.rect(screen, BLACK, rect.inflate(-1, -1), 1)
            pygame.draw.rect(screen, color, rect.inflate(-2, -2))


def draw_next_piece(screen, piece):
    x_c, y_c = 27, 11

    # # Determine the bounding box of the piece
    # min_x = min(point[0] for point in piece.body)
    # max_x = max(point[0] for point in piece.body)
    # min_y = min(point[1] for point in piece.body)
    # max_y = max(point[1] for point in piece.body)

    # # Calculate the rectangle coordinates to enclose the piece
    # rect = pygame.Rect((x_c + min_x - 1) * BLOCK_SIZE, (y_c - max_y) * BLOCK_SIZE,
    #                    (max_x - min_x + 3) * BLOCK_SIZE, (max_y - min_y + 3) * BLOCK_SIZE)

    # Draw the rectangle border
    # pygame.draw.rect(screen, GRAY, rect, 1)

    for point in piece.body:
        rect = pygame.Rect((27 + point[0]) * BLOCK_SIZE, (12 - point[1]) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, GRAY, rect, 1)
        pygame.draw.rect(screen, BLACK, rect.inflate(-1, -1), 1)
        pygame.draw.rect(screen, piece.color, rect.inflate(-2, -2))


def draw_boards(screen, board):
    draw_grid(screen, board, MINI_BLOCK, 5, -4)
    draw_grid(screen, board, MINI_BLOCK, 5, -57)

    draw_grid(screen, board, MINI_BLOCK, 69, -4)
    draw_grid(screen, board, MINI_BLOCK, 69, -57)
    draw_grid(screen, board, BLOCK_SIZE, 16, -11)


def recv_data(sock):
    data, addr = sock.recvfrom(BUFFER_SIZE)
    return pickle.loads(data)


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind((MY_IP, MY_PORT))
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Server")
    clock = pygame.time.Clock()
    # Initialize board and state
    board = Board()
    state = State(board)

    # draw the screen
    screen.fill(WHITE)
    draw_boards(screen, board)
    pygame.display.flip()

    game_over = False
    while not game_over:

        received = recv_data(my_socket)
        state = received if received else board

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        screen.fill(WHITE)
        draw_boards(screen, state.board)
        pygame.display.flip()

        game_over = state.game_over

    # time.sleep(3)
    # for row in reversed(state.board.board):
    #     for element in row:
    #         print(element, end=" ")
    #     print()
    # print()
    pygame.quit()


if __name__ == "__main__":
    main()
