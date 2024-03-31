# Import your classes
import time

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


def draw_grid(screen, board, size, start_x, start_y):
    for y, row in enumerate(board.board):
        for x, cell in enumerate(row):
            color = cell
            rect = pygame.Rect((start_x + x) * size, (HEIGHT - start_y - y - 1) * size, size, size)
            pygame.draw.rect(screen, GRAY, rect, 1)
            pygame.draw.rect(screen, BLACK, rect.inflate(-1, -1), 1)
            pygame.draw.rect(screen, color, rect.inflate(-2, -2))


def main():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    drop_time = 0

    # Initialize board and state
    board = Board()
    state = State(board)
    state.generate_new_piece()
    state.board.place(state.x, state.y, state.current_piece)

    # draw the screen
    screen.fill(WHITE)
    draw_grid(screen, board, MINI_BLOCK, 5, -4)
    draw_grid(screen, board, MINI_BLOCK, 5, -57)

    draw_grid(screen, board, MINI_BLOCK, 69, -4)
    draw_grid(screen, board, MINI_BLOCK, 69, -57)
    draw_grid(screen, board, BLOCK_SIZE, 16, -11)

    pygame.display.flip()

    game_over = False
    while not game_over:

        dt = clock.tick(60)  # Cap the frame rate at 60 FPS
        drop_time += dt
        state.shift_x = 0  # each frame x is reset
        pressed = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                pressed = True
                last_chance = True
                if event.key == pygame.K_LEFT:
                    state.shift_x -= 1
                    state.move_x()
                elif event.key == pygame.K_RIGHT:
                    state.shift_x += 1
                    state.move_x()
                elif event.key == pygame.K_UP:
                    state.rotate()

        if drop_time >= 100:  # Half-second interval
            drop_time = 0
            state.shift_x = 0
            game_over = state.move_y(pressed)

        screen.fill(WHITE)
        draw_grid(screen, board, MINI_BLOCK, 5, -4)
        draw_grid(screen, board, MINI_BLOCK, 5, -57)

        draw_grid(screen, board, MINI_BLOCK, 69, -4)
        draw_grid(screen, board, MINI_BLOCK, 69, -57)
        draw_grid(screen, board, BLOCK_SIZE, 16, -11)

        pygame.display.flip()

    time.sleep(3)
    for row in reversed(state.board.board):
        for element in row:
            print(element, end=" ")
        print()
    print()
    pygame.quit()


if __name__ == "__main__":
    main()
