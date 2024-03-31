# Import your classes
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

    running = True
    while running:
        screen.fill(WHITE)
        draw_grid(screen, board, MINI_BLOCK, 5, -4)
        draw_grid(screen, board, MINI_BLOCK, 5, -57)

        draw_grid(screen, board, MINI_BLOCK, 69, -4)
        draw_grid(screen, board, MINI_BLOCK, 69, -57)
        draw_grid(screen, board, BLOCK_SIZE, 16, -11)

        pygame.display.flip()

        dt = clock.tick(60)  # Cap the frame rate at 60 FPS
        drop_time += dt
        state.shift_x = 0 # each frame x is reset

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    state.shift_x -= 1
                    state.move_piece()
                elif event.key == pygame.K_RIGHT:
                    state.shift_x += 1
                    state.move_piece()

        if drop_time >= 500:  # Half-second interval
            drop_time = 0
            state.shift_x = 0
            state.move_piece()


if __name__ == "__main__":
    main()
