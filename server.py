# Import your classes
import hashlib
import pickle
import random
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

start_game = threading.Event()
end_game = threading.Event()

MEMORY_SIZE = (4 * 3) * 10 * 20
ID_SIZE = 256

# boards_lock = threading.Lock()
addr_lock = threading.Lock()
addresses = {}
# ids = []
lines_to_send = {}


def generate_unique_id(ip, port):
    # Concatenate IP address and port as a string
    combined_str = f"{ip}:{port}"

    # Hash the combined string using SHA-256 (you can choose a different hash function if needed)
    hashed = hashlib.sha256(combined_str.encode()).hexdigest()

    return hashed


def handle_client(sock, addr):
    global addresses
    global lines_to_send
    try:
        a = receive_tcp(sock).decode()
        if re.search(r"^LISTEN ON (\d+)", a) is None:
            return
        player_address = (addr[0], int(''.join(filter(str.isdigit, a))))
        player_id = generate_unique_id(addr[0], addr[1])
        with addr_lock:
            addresses[player_address] = player_id
            # ids.append(player_id)
            lines_to_send[player_id] = 0
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
            lines = 0
            with addr_lock:
                if lines_to_send[player_id] != 0:
                    lines = lines_to_send[player_id]
                    print(lines)
                    lines_to_send[player_id] = 0
            if lines != 0:
                print(f"sending: {lines}")
                print(f"my id is: {player_id}")

                print(struct.pack(PACK_SIGN, socket.htonl(lines)))
                threading.Thread(target=send_tcp,
                                 args=(sock, struct.pack(PACK_SIGN, socket.htonl(lines)))).start()
            a = receive_tcp(sock)

            if a != b'':
                a = a.split(b'|')
                print(a)
                lines_to_add = socket.htonl(struct.unpack(PACK_SIGN, a[0])[0])
                print(f"need to add {lines_to_add}")
                print(f"my id is: {player_id}")
                with addr_lock:
                    filtered_keys = [key for key in lines_to_send.keys() if key != player_id]
                    print(filtered_keys[0])
                    lines_to_send[random.choice(filtered_keys)] += lines_to_add
                game_over = struct.unpack('?', a[1])[0]
            elif a == b'ERROR':
                game_over = True
        with addr_lock:
            del addresses[player_address]
            ids.remove(player_id)

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
    if addr in addresses.keys():
        send_id = addresses[addr]
        # data = pickle.dumps(board)
        for s_ad, s_id in addresses.items():
            if s_ad != addr:
                # print("hey?")
                try:
                    msg = send_id.encode() + board

                    sock.sendto(msg, s_ad)
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
    backlog = 3  # Maximum number of queued connections

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
        client_socket.settimeout(1)
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
