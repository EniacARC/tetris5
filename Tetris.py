# Import your classes
import pickle
import random
import struct
import threading
import time
import socket
import pygame
from board import Board
from piece import Piece
from state import State
import struct
from collections import OrderedDict
from comms import *

# --- gui constants ---
BLOCK_SIZE = 24
MINI_BLOCK = 24 // 2
WIDTH = 10  # Number of columns
HEIGHT = 20  # Number of rows
WINDOW_SIZE = (1008, 1008)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)

NUM_OF_OPPS = 4

# --- coms constants ---
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
S_UDP = 7372
BUFFER_SIZE = 2048

LISTEN_IP = '0.0.0.0'
LISTEN_PORT = random.randrange(2000, 2100)

# --- msg ---
READY_MSG = "READY"
START_SIGNAL = "START"
# define global vars
# -- events ---
change_event = threading.Event()
# data_received_event = threading.Event()

# --- locks ---
data_lock = threading.Lock()
# --- game global ---
game_over = False  # set game to be true
received_data = None

boards_lock = threading.Lock()
boards = {}

MEMORY_SIZE_BOARD = (4 * 3) * 10 * 20
ID_SIZE = 64

MINI_BOARDS_POS = [(5, -4), (5, -57), (69, -4), (69, -57)]

# MINI_BOARDS_POS = [(5, -4), (5, -57), (69, -4), (69, -57)]
# lock = threading.Lock()
# event_glob = threading.Event()
# key = ""


def draw_grid(screen, board, size, start_x, start_y):
    for y, row in enumerate(board):
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


# def draw_other_player(screen, board, pos):
#     draw_grid(screen, board, MINI_BLOCK, MINI_BOARDS_POS[pos][0], MINI_BOARDS_POS[pos][1])


def draw_board(screen, board):
    # draw_grid(screen, board, MINI_BLOCK, 5, -4)
    # draw_grid(screen, board, MINI_BLOCK, 5, -57)
    #
    # draw_grid(screen, board, MINI_BLOCK, 69, -4)
    # draw_grid(screen, board, MINI_BLOCK, 69, -57)
    draw_grid(screen, board, BLOCK_SIZE, 16, -11)


def receive_updates_tcp(sock):
    global received_data
    while not game_over:
        try:
            data = receive_tcp(sock)
            if data != b'':
                with data_lock:
                    received_data = data
                # data_received_event.set()
            else:
                print("empty tcp")
        except socket.error as err:
            print(f"error while receiving update: {err}")


def send_update_tcp(sock, lines, g_over):
    data = struct.pack(PACK_SIGN, socket.htonl(lines))
    data += b'|'
    data += struct.pack('?', g_over)
    print(f"sending to server: {data}")
    # print(struct.pack('?', g_over))

    send_tcp(sock, data)


def establish_connection(sock):
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
        send_tcp(sock, f"LISTEN ON {LISTEN_PORT}".encode())
        a = receive_tcp(sock)
        while a != "START".encode():
            send_tcp(sock, READY_MSG.encode())
            a = receive_tcp(sock)
        return True
    except socket.error as err:
        print(f"error while connection to server: {err}")
        return False


def send_data_udp(sock, data):
    # global game_over
    # while not game_over:
    #     change_event.wait()
    try:
        serialized_data = pickle.dumps(data)
        serialized_data = serialized_data.ljust(MEMORY_SIZE_BOARD, b'\0')
        sock.sendto(serialized_data, (SERVER_IP, S_UDP))
        # print("send update")
    except socket.error as err:
        print(f"error! '{err}'")
    # finally:
    #     change_event.clear()


def get_data_udp(sock):
    global boards
    while not game_over:
        try:
            data, addr = recv_udp(sock, MEMORY_SIZE_BOARD + ID_SIZE)

            # print(data)
            if data != b'':
                with boards_lock:
                    print(data[:ID_SIZE])
                    boards[data[:ID_SIZE]] = pickle.loads(data[ID_SIZE:])

            else:
                print("empty udp")
        except socket.error as err:
            print(f"error while receiving update udp: {err}")


def main():
    global game_over
    global received_data
    # --- define initial game states ---
    # ----------------------------------
    # ~ coms ~
    # set udp socket
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', LISTEN_PORT))
    udp_sock.settimeout(1)
    print(LISTEN_PORT)

    # set tcp socket
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.settimeout(1)
    game_over = not establish_connection(tcp_sock)
    # tcp_sock.connect((SERVER_IP, SERVER_PORT))

    # ~ gui ~
    # start pygame
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Tetris")

    # set variables for time
    clock = pygame.time.Clock()
    drop_time = 0
    press_time = 0

    # set start states for all the keys
    pressed_keys = {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False}

    # ~ game logic ~
    # Initialize board and state
    empty_board = Board().board
    board = Board()
    state = State(board)

    # create first piece
    state.generate_new_piece()
    state.board.place(state.x, state.y, state.current_piece)

    # draw the screen
    screen.fill(WHITE)
    draw_board(screen, board.board)
    draw_next_piece(screen, state.next)
    pygame.display.flip()

    # ~ threads ~
    if not game_over:
        recv_lines_thread = threading.Thread(target=receive_updates_tcp, args=(tcp_sock,))
        recv_lines_thread.start()
        recv_boards_thread = threading.Thread(target=get_data_udp, args=(udp_sock,))
        recv_boards_thread.start()
    # send_thread = threading.Thread(target=send_data, args=(udp_sock, state))
    # send_thread.start()

    state.add_lines(1)
    state.add_lines(1)
    state.add_lines(1)
    cleared_before = 0
    cleared_current = 0
    while not game_over:

        change = False  # if change happened, update the server
        dt = clock.tick(60)  # Cap the frame rate at 60 FPS

        # add time passed
        drop_time += dt
        press_time += dt
        state.shift_x = 0  # each frame x is reset
        lines_to_add = 0  # how many lines player got sent

        with data_lock:
            if received_data:
                print("received data")
                state.add_lines(socket.htonl(struct.unpack(PACK_SIGN, received_data)[0]))
                received_data = None

        for event in pygame.event.get():
            change = True
            if event.type == pygame.QUIT:
                # change = True
                game_over = True
            # Track key presses and releases
            elif event.type == pygame.KEYDOWN:
                # change = True
                state.grace = state.grace_turns
                if event.key == pygame.K_UP:
                    state.rotate()
                else:
                    pressed_keys[event.key] = True

            elif event.type == pygame.KEYUP:
                pressed_keys[event.key] = False

        # Handle continuous movement
        if press_time >= 50:

            press_time = 0
            if pressed_keys.get(pygame.K_LEFT):
                change = True
                state.shift_x -= 1
                state.move_x()
            elif pressed_keys.get(pygame.K_RIGHT):
                change = True
                state.shift_x += 1
                state.move_x()
            elif pressed_keys.get(pygame.K_DOWN):
                change = True
                state.move_y()
                # game_over = state.game_over

        # it's time to drop the piece down
        if drop_time >= 100:
            change = True
            drop_time = 0
            state.shift_x = 0
            state.move_y()

            cleared_before = cleared_current
            cleared_current = state.board.cleared
            if cleared_before != cleared_current:
                send_lines_thread = threading.Thread(target=send_update_tcp(tcp_sock,
                                                                            cleared_current - cleared_before,
                                                                            game_over))
                send_lines_thread.start()

            game_over = state.game_over

        # --- draw the new screen ---
        # clear the screen
        screen.fill(WHITE)

        # draw other boards:
        # ~ temp ~
        # ---
        # draw_grid(screen, board.board, MINI_BLOCK, 5, -4)
        # draw_grid(screen, board.board, MINI_BLOCK, 5, -57)
        #
        # draw_grid(screen, board.board, MINI_BLOCK, 69, -4)
        # draw_grid(screen, board.board, MINI_BLOCK, 69, -57)
        # ---

        # draw the player and next piece
        draw_board(screen, board.board)
        draw_next_piece(screen, state.next)
        with boards_lock:
            for i, n in boards.items():
                print(i)
            empty = NUM_OF_OPPS
            for i in boards.values():
                # for row in (i):
                #     for element in row:
                #         print(element, end=" ")
                #     print()
                # print()
                draw_grid(screen, i, MINI_BLOCK, MINI_BOARDS_POS[empty-1][0], MINI_BOARDS_POS[empty-1][1])
                empty = empty - 1
            for i in range(empty):
                draw_grid(screen, empty_board, MINI_BLOCK, MINI_BOARDS_POS[i][0], MINI_BOARDS_POS[i][1])

        # commit the new screen
        pygame.display.flip()

        if change:
            # send the new board
            # change_event.set()
            update_board_thread = threading.Thread(target=send_data_udp, args=(udp_sock, board.board))
            update_board_thread.start()
            # send_data(udp_sock, state.board)
    print("done")
    # send_thread.join()
    send_update_tcp(tcp_sock, 0, True)  # tell server you finished playing
    time.sleep(3)
    pygame.quit()
    tcp_sock.close()


if __name__ == "__main__":
    main()
