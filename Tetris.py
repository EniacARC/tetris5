# Import your classes
import pickle
import struct
import threading
import time
import socket
import pygame
from board import Board
from piece import Piece
from state import State

from collections import OrderedDict

# Constants
BLOCK_SIZE = 24
MINI_BLOCK = 24 // 2
WIDTH = 10  # Number of columns
HEIGHT = 20  # Number of rows
WINDOW_SIZE = (1008, 1008)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7372
BUFFER_SIZE = 2048

MINI_BOARDS_POS = [(5, -4), (5, -57), (69, -4), (69, -57)]
lock = threading.Lock()
event_glob = threading.Event()
key = ""


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


def draw_other_player(screen, board, pos):
    draw_grid(screen, board, MINI_BLOCK, MINI_BOARDS_POS[pos][0], MINI_BOARDS_POS[pos][1])


def draw_board(screen, board):
    # draw_grid(screen, board, MINI_BLOCK, 5, -4)
    # draw_grid(screen, board, MINI_BLOCK, 5, -57)
    #
    # draw_grid(screen, board, MINI_BLOCK, 69, -4)
    # draw_grid(screen, board, MINI_BLOCK, 69, -57)
    draw_grid(screen, board, BLOCK_SIZE, 16, -11)


def send_data(sock, data):
    b = pickle.dumps(data.board)
    # g = struct.pack('?', data.game_over)
    # to_send = b + b'|||' + g
    sock.sendto(b, (SERVER_IP, SERVER_PORT))


def update_player(players, id_code, board):
    with lock:
        players[id_code] = board


def recv_data(sock, players):
    # the game over is temporary and will be sent through tcp
    while not event_glob.is_set():
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            if data:
                data = data.split(b'|||')  # id, board
                update_player(players, data[0].decode(), pickle.loads(data[1]))
        except socket.error as err:
            pass
            # data = data.split(b'|||')
            # return pickle.loads(data[0]), struct.unpack('?', data[1])[0]


def establish_connection(sock):
    global key
    while key == '':
        try:
            sock.connect(("127.0.0.1", 12345))
            key_add = ''
            while True:
                buff = sock.recv(1).decode()
                if buff == '':
                    break
                key_add += buff
            print(key_add)
            key = key_add
        except socket.error as err:
            key = ''


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind(('0.0.0.0', 1234))

    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    establish_connection(tcp_sock)

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    drop_time = 0
    press_time = 0
    pressed_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False}

    # Initialize board and state
    board = Board()
    state = State(board)
    state.generate_new_piece()
    state.board.place(state.x, state.y, state.current_piece)

    temp_board = Board()

    # create the players list
    players = OrderedDict()  # made up from (id, board)

    players_thread = threading.Thread(target=recv_data, args=(my_socket, players))
    players_thread.start()

    # draw the screen
    screen.fill(WHITE)
    draw_board(screen, board)
    draw_next_piece(screen, state.next)

    for i in range(4):
        draw_other_player(screen, board, i)

    pygame.display.flip()

    game_over = False

    # send_interval = 1 / 60

    while not game_over:
        # every cycle send update
        send_thread = threading.Thread(target=send_data, args=(my_socket, state))
        send_thread.start()

        # send_data(my_socket, state)
        dt = clock.tick(60)  # Cap the frame rate at 60 FPS
        drop_time += dt
        press_time += dt
        state.shift_x = 0  # each frame x is reset

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            # Track key presses and releases
            elif event.type == pygame.KEYDOWN:
                state.grace = state.grace_turns
                if event.key == pygame.K_UP:
                    state.rotate()
                else:
                    pressed_keys[event.key] = True
                # pressed = True

            elif event.type == pygame.KEYUP:
                pressed_keys[event.key] = False

        if press_time >= 50:
            press_time = 0
            # Handle continuous movement
            if pressed_keys.get(pygame.K_LEFT):
                state.shift_x -= 1
                state.move_x()
            elif pressed_keys.get(pygame.K_RIGHT):
                state.shift_x += 1
                state.move_x()
            elif pressed_keys.get(pygame.K_DOWN):
                state.move_y()

        if drop_time >= 100:
            drop_time = 0
            state.shift_x = 0
            state.move_y()
            game_over = state.game_over

        screen.fill(WHITE)
        draw_board(screen, board)
        draw_next_piece(screen, state.next)

        with lock:
            for index, (id_code, board_player) in enumerate(players.items()):
                draw_other_player(screen, board_player, index)
            for i in range(4 - len(players)):
                draw_other_player(screen, temp_board, i)

        pygame.display.flip()

        send_thread.join()

    print("done")
    event_glob.set()
    send_data(my_socket, state)
    players_thread.join()
    time.sleep(3)
    # for row in reversed(state.board.board):
    #     for element in row:
    #         print(element, end=" ")
    #     print()
    # print()
    tcp_sock.close()
    pygame.quit()


if __name__ == "__main__":
    main()
