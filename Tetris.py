# Import your classes
import pickle
import random
import threading
import time
import pygame
from board import Board
from state import State
from comms import *

# --- gui constants ---
BLOCK_SIZE = 24
MINI_BLOCK = 24 // 2
WIDTH = 10  # Number of columns
HEIGHT = 20  # Number of rows
WINDOW_SIZE = (1008, 1008)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

MAIN_BOARD = (16, -11)
MINI_BOARDS_POS = [(5, -4), (5, -57), (69, -4), (69, -57)]
NUM_OF_OPPS = 4

# --- coms constants ---
SERVER_IP = '127.0.0.1'
SERVER_PORT_TCP = 12345
SERVER_PORT_UDP = 7372

MEMORY_SIZE_BOARD = (4 * 3) * 10 * 20
ID_SIZE = 64

LISTEN_IP = '0.0.0.0'
LISTEN_PORT_UDP = random.randrange(2000, 2100)

# --- msg ---
FIRST_CONNECTION_MSG = f"LISTEN ON {LISTEN_PORT_UDP}"
READY_MSG = "READY"
START_SIGNAL = "START"
# define global vars
# -- events ---
change_event = threading.Event()

# --- locks ---
data_lock = threading.Lock()
boards_lock = threading.Lock()

# --- game global ---
game_over = False  # set game to be true
received_data = None
boards = {}

TYPE_LINES = b'L'
TYPE_GAME_OVER = b'G'
TYPE_WON = b'W'

EMPTY_BOARD = Board().board
ELIMINATE_PHOTO_ADDR = "sprites/eliminated_sprite.png"
WIN_PHOTO_ADDR = "sprites/win_screen.png"
TILE_SET_ADDR = "sprites/tiles.png"
NEXT_ADDR = "sprites/next_sprite.png"


def draw_grid(screen, board, start_x, start_y, size, tile_set):
    """
    Draws the grid on the screen based on the provided board.

    :param screen: The surface to draw the grid on.
    :type screen: pygame.Surface
    :param board: The 2D array representing the game board.
    :type board: list of lists
    :param start_x: The starting x-coordinate of the grid on the screen.
    :type start_x: int
    :param start_y: The starting y-coordinate of the grid on the screen.
    :type start_y: int
    :param size: The size of each tile in pixels.
    :type size: int
    :param tile_set: The image containing the tiles to draw.
    :type tile_set: pygame.Surface

    :return: None
    """
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            cords = (start_x + x) * size, (HEIGHT - start_y - y - 1) * size
            tile = (cell * size, 0, size, size)
            screen.blit(tile_set, cords, tile)


def draw_next_piece(screen, piece, tile_set, img):
    """
    Draws the next piece on the screen.

    :param screen: The surface to draw the piece on.
    :type screen: pygame.Surface
    :param piece: The Tetris piece to draw.
    :type piece: piece.Piece
    :param tile_set: The image containing the tiles to draw.
    :type tile_set: pygame.Surface
    :param img: the next sprite
    :type img: pygame.Surface

    :return: None
    """
    tile = piece.color * BLOCK_SIZE, 0, BLOCK_SIZE, BLOCK_SIZE

    img_cords = 26 * BLOCK_SIZE, 9 * BLOCK_SIZE
    screen.blit(img, img_cords)
    for point in piece.body:
        cords = (27 + point[0]) * BLOCK_SIZE, (12 - point[1]) * BLOCK_SIZE
        border = pygame.Rect(*cords, BLOCK_SIZE, BLOCK_SIZE)
        screen.blit(tile_set, cords, tile)
        pygame.draw.rect(screen, BLACK, border, 1)


def draw_board(screen, board, tile_set):
    """
    Draws the game board on the screen.

    :param screen: The surface to draw the board on.
    :type screen: pygame.Surface
    :param board: The 2D array representing the game board.
    :type board: list of lists
    :param tile_set: The image containing the tiles to draw.
    :type tile_set: pygame.Surface

    :return: None
    """
    draw_grid(screen, board, MAIN_BOARD[0], MAIN_BOARD[1], BLOCK_SIZE, tile_set)


def receive_updates_tcp(sock):
    """
    Receive updates over TCP socket and store them in a global variable.

    :param sock: The TCP socket to receive updates from.
    :type sock: socket.socket

    :return: None
    """
    global received_data
    while not game_over:
        try:
            data = receive_tcp(sock)
            if data != b'':
                with data_lock:
                    received_data = data
        except socket.error as err:
            print(f"error while receiving update: {err}")


def send_update_tcp(sock, lines, g_over):
    """
    Send updates over TCP socket to the server.

    :param sock: The TCP socket to send updates through.
    :type sock: socket.socket
    :param lines: The number of lines cleared in the game.
    :type lines: int
    :param g_over: A boolean indicating whether the game is over or not.
    :type g_over: bool

    :return: None
    """
    data = struct.pack(PACK_SIGN, socket.htonl(lines))
    data += b'|'
    data += struct.pack('?', g_over)
    print(f"sending to server: {data}")

    send_tcp(sock, data)


def establish_connection(sock):
    """
    Establish a connection to the server.

    :param sock: The socket to establish the connection with.
    :type sock: socket.socket

    :return: A boolean indicating whether the connection was successfully established or not.
    :rtype: bool
    """
    try:
        sock.connect((SERVER_IP, SERVER_PORT_TCP))
        if send_tcp(sock, FIRST_CONNECTION_MSG.encode()):
            a = receive_tcp(sock)
            while a != "START".encode():
                if not send_tcp(sock, READY_MSG.encode()):
                    return False
                a = receive_tcp(sock)
            return True
    except socket.error as err:
        print(f"error while connection to server: {err}")
        return False


def send_data_udp(sock, data):
    """
    Send data over UDP socket to the server.

    :param sock: The UDP socket to send data through.
    :type sock: socket.socket
    :param data: The data to be sent.
    :type data: Any

    :return: None
    """
    try:
        serialized_data = pickle.dumps(data)
        serialized_data = serialized_data.ljust(MEMORY_SIZE_BOARD, b'\0')
        sock.sendto(serialized_data, (SERVER_IP, SERVER_PORT_UDP))
    except socket.error as err:
        print(f"error! '{err}'")


def get_data_udp(sock):
    """
    Receive data over UDP socket and store it in a global variable.

    :param sock: The UDP socket to receive data from.
    :type sock: socket.socket

    :return: None
    """
    global boards
    while not game_over:
        try:
            data, addr = recv_udp(sock, MEMORY_SIZE_BOARD + ID_SIZE)
            if data != b'':
                with boards_lock:
                    boards[data[:ID_SIZE]] = pickle.loads(data[ID_SIZE:])
        except socket.error as err:
            # print(f"error while receiving update udp: {err}")
            pass


def calculate_eliminate_cords(x_cord, y_cord):
    return x_cord * MINI_BLOCK, (HEIGHT - y_cord - 15) * MINI_BLOCK


def main():
    """
    the main function; responsible for running the client code.
    """
    global game_over
    global received_data
    global boards
    # --- define initial game states ---
    # ----------------------------------
    # ~ coms ~
    # set udp socket
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((LISTEN_IP, LISTEN_PORT_UDP))
    udp_sock.setblocking(False)  # set timeout for so recv isn't blocking

    # set tcp socket
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.settimeout(1)  # set timeout for so recv isn't blocking

    # check if we connected to the server
    if not establish_connection(tcp_sock):
        return

    # ~ gui ~
    # start pygame
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Tetris")

    # set variables for time
    clock = pygame.time.Clock()
    drop_time = 0
    press_time = 0

    # sprites
    tile_set = pygame.image.load(TILE_SET_ADDR).convert_alpha()
    mini_tile_set = pygame.image.load(TILE_SET_ADDR).convert_alpha()
    tile_set_width, tile_set_height = tile_set.get_size()
    mini_tile_set = pygame.transform.scale(mini_tile_set, (tile_set_width // 2, tile_set_height // 2))

    eliminate_img = pygame.image.load(ELIMINATE_PHOTO_ADDR).convert_alpha()
    win_img = pygame.image.load(WIN_PHOTO_ADDR).convert_alpha()
    next_img = pygame.image.load(NEXT_ADDR).convert_alpha()
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
    draw_board(screen, board.board, tile_set)
    draw_next_piece(screen, state.next, tile_set, next_img)
    pygame.display.flip()

    # set variables for lines
    cleared_before = 0
    cleared_current = 0

    # ~ threads ~
    if not game_over:
        recv_lines_thread = threading.Thread(target=receive_updates_tcp, args=(tcp_sock,))
        recv_lines_thread.start()
        recv_boards_thread = threading.Thread(target=get_data_udp, args=(udp_sock,))
        recv_boards_thread.start()

    while not game_over:
        change = False  # if change happened, update the server
        dt = clock.tick(60)  # Cap the frame rate at 60 FPS

        # add time passed
        drop_time += dt
        press_time += dt
        state.shift_x = 0  # each frame x is reset
        lines_to_add = 0  # how many lines player got sent

        for event in pygame.event.get():
            change = True
            if event.type == pygame.QUIT:
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

        # draw the player and next piece
        draw_board(screen, board.board, tile_set)
        draw_next_piece(screen, state.next, tile_set, next_img)

        # draw other players:
        with boards_lock:
            empty = NUM_OF_OPPS
            for i in boards.values():
                if i:
                    draw_grid(screen, i, MINI_BOARDS_POS[empty - 1][0], MINI_BOARDS_POS[empty - 1][1],
                              MINI_BLOCK, mini_tile_set)
                else:
                    draw_grid(screen, EMPTY_BOARD, MINI_BOARDS_POS[empty - 1][0], MINI_BOARDS_POS[empty - 1][1],
                              MINI_BLOCK, mini_tile_set)
                    screen.blit(eliminate_img,
                                calculate_eliminate_cords(MINI_BOARDS_POS[empty - 1][0], MINI_BOARDS_POS[empty - 1][1]))
                empty = empty - 1
            for i in range(empty):
                draw_grid(screen, empty_board, MINI_BOARDS_POS[i][0], MINI_BOARDS_POS[i][1],
                          MINI_BLOCK, mini_tile_set)

        # commit the new screen
        pygame.display.flip()

        if change:
            update_board_thread = threading.Thread(target=send_data_udp, args=(udp_sock, board.board))
            update_board_thread.start()

        with data_lock:
            if received_data:
                msg_type = received_data[0:1]
                data = received_data[1:]

                if msg_type == TYPE_LINES:
                    state.add_lines(socket.htonl(struct.unpack(PACK_SIGN, data)[0]))
                elif msg_type == TYPE_GAME_OVER:
                    with boards_lock:
                        boards[data] = None
                elif msg_type == TYPE_WON:
                    pygame.display.flip()
                    time.sleep(1)
                    screen.blit(win_img, (0, 0))
                    pygame.display.flip()
                    break

                received_data = None

    if game_over:
        data = struct.pack(PACK_SIGN, socket.htonl(0))
        data += b'|'
        data += struct.pack('?', True)
        sent = send_tcp(tcp_sock, data)
        while not sent:
            sent = send_tcp(tcp_sock, data)
    else:
        game_over = True
    time.sleep(3)
    pygame.quit()
    tcp_sock.close()


if __name__ == "__main__":
    main()
