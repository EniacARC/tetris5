# Import your classes
import hashlib
import pickle
import struct
import threading
import time
import socket
from collections import OrderedDict

import pygame
from board import Board
from piece import Piece
from state import State
from comms import *
import pickle
import re

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

MINI_BOARDS_POS = [(5, -4), (5, -57), (69, -4), (69, -57)]

start_game = threading.Event()
end_game = threading.Event()

MEMORY_SIZE = (4 * 3) * 10 * 20
ID_SIZE = 256

# boards_lock = threading.Lock()
addr_lock = threading.Lock()
addresses = []
ids = []


def generate_unique_id(ip, port):
    # Concatenate IP address and port as a string
    combined_str = f"{ip}:{port}"

    # Hash the combined string using SHA-256 (you can choose a different hash function if needed)
    hashed = hashlib.sha256(combined_str.encode()).hexdigest()

    return hashed


def handle_client(sock, addr):
    global addresses
    try:
        a = receive_tcp(sock).decode()
        if re.search(r"^LISTEN ON (\d+)", a) is None:
            return
        with addr_lock:
            addresses.append((addr[0], int(''.join(filter(str.isdigit, a)))))
            ids.append(generate_unique_id(addr[0], addr[1]))
        while not start_game.is_set():
            send_tcp(sock, "READY".encode())
            if receive_tcp(sock).decode() != "READY":
                print("unresponsive")
                return

        # start_game.wait()

        send_tcp(sock, "START".encode())

        lines_to_add = 0
        game_over = False

        while not game_over:
            a = receive_tcp(sock)
            print(a)
            if a == b'':
                return
            a = a.split(b'|')
            lines_to_add = socket.htonl(struct.unpack(PACK_SIGN, a[0])[0])
            game_over = struct.unpack('?', a[1])[0]
    except socket.error as err:
        print(f"error: {err}")


def draw_grid(screen, board, size, start_x, start_y):
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            color = cell
            rect = pygame.Rect((start_x + x) * size, (HEIGHT - start_y - y - 1) * size, size, size)
            pygame.draw.rect(screen, GRAY, rect, 1)
            pygame.draw.rect(screen, BLACK, rect.inflate(-1, -1), 1)
            pygame.draw.rect(screen, color, rect.inflate(-2, -2))


def draw_board(screen, board):
    # draw_grid(screen, board, MINI_BLOCK, 5, -4)
    # draw_grid(screen, board, MINI_BLOCK, 5, -57)
    #
    # draw_grid(screen, board, MINI_BLOCK, 69, -4)
    # draw_grid(screen, board, MINI_BLOCK, 69, -57)
    draw_grid(screen, board, BLOCK_SIZE, 16, -11)


def send_board(sock, addr, board):
    # print(f"sending {board}")
    if addr in addresses:
        # data = pickle.dumps(board)
        for i in range(len(addresses)):
            if addresses[i] != addr:
                # print("hey?")
                try:
                    msg = ids[i].encode() + board

                    sock.sendto(msg, addresses[i])
                    # print(f"sent to {addresses[i]}")
                except socket.error as err:
                    print(f"error while updating player at {addresses[i]}")
                    # addresses.remove(address) # something was wrong with the connection
                    # set address to game_over


def receive_boards(sock):
    while not end_game.is_set():
        try:
            data, addr = recv_udp(sock, MEMORY_SIZE)
            if data != b'':
                # data = pickle.loads(data)
                # print(f"recv from {addr}")
                # for addr in addresses:
                #     print(addr)
                send_board_thread = threading.Thread(target=send_board, args=(sock, addr, data))
                send_board_thread.start()
        except socket.error as err:
            pass


# Game logic goes here


def main():
    global addresses
    global ids
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind((MY_IP, MY_PORT))
    my_socket.settimeout(1)
    # Server configuration
    host = '0.0.0.0'
    port = 12345
    backlog = 2  # Maximum number of queued connections

    t1 = threading.Thread(target=receive_boards, args=(my_socket,))
    t1.start()

    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    server_socket.bind((host, port))

    # Start listening for incoming connections
    server_socket.listen(backlog)
    print(f"Server listening on {host}:{port}")

    # connected_clients = []
    # client_threads = []

    clients = []

    # Accept connections
    while len(clients) < backlog:

        client_socket, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        clients.append((address, client_thread))
        client_thread.start()

        for client in clients:
            if not client[1].is_alive():
                clients.remove(client)

    # for i in range(len(clients)):
    #     addresses.append(clients[i][0])
    #     ids.append(generate_unique_id(clients[i][0][0], clients[i][0][1]))

    # print(addresses)

    start_game.set()

    # # Start handling clients only after all players are connected
    # client_threads = []
    # for client_socket, address in connected_clients:
    #     client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
    #     client_threads.append(client_thread)
    #     client_thread.start()

    # Wait for all client threads to complete
    for client in clients:
        client[1].join()

    print("game ended")

    end_game.set()

    # Close the server socket
    server_socket.close()


if __name__ == "__main__":
    main()
