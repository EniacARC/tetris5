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

lock = threading.Lock()

start_game = threading.Event()

MEMORY_SIZE = (4 * 3) * 10 * 20


def recv_data(sock):
    # the game over is temporary and will be sent through tcp

    data, addr = sock.recvfrom(BUFFER_SIZE)
    data = data.split(b'|||')
    return pickle.loads(data[0]), struct.unpack('?', data[1])[0]


def send_data(sock, addr, data):
    b = pickle.dumps(data.board)
    g = struct.pack('?', data.game_over)
    to_send = b + b'|||' + g
    sock.sendto(to_send, addr)


def update_client(clients, addr, data):
    with lock:
        clients[addr] = data


def send_states(interval, sock, clients):
    while True:
        print("h")
        with lock:
            for i in range(len(clients)):
                for j in range(len(clients)):
                    if i != j:
                        send_data(sock, clients[j][0], clients[i][1])
        #     if clients:
        #         for client in clients.items():
        #             for addr in clients.keys():
        #                 if addr != client:
        #                     send_data(sock, addr, client[1])
        # time.sleep(interval)


def generate_unique_id(ip, port):
    # Concatenate IP address and port as a string
    combined_str = f"{ip}:{port}"

    # Hash the combined string using SHA-256 (you can choose a different hash function if needed)
    hashed = hashlib.sha256(combined_str.encode()).hexdigest()

    return hashed


def handle_client(sock, addr):
    try:
        if receive_tcp(sock).decode() != "READY":
            return

        start_game.wait()

        send_tcp(sock, "START".encode())

        lines_to_add = 0
        game_over = False

        while not game_over:
            a = receive_tcp(sock)
            if a == b'':
                return
            a = a.split(b'|')
            lines_to_add = socket.htonl(struct.unpack(PACK_SIGN, a[0])[0])
            game_over = struct.unpack('?', a[1])[0]
    except socket.error as err:
        print(f"error: {err}")


# print("welcome player!")
# player_code = generate_unique_id(addr[0], addr[1]).encode()
# sent = 0
# try:
#     # send message length
#     while sent < len(player_code):
#         sent += sock.send(player_code[sent:])
# except socket.error as err:
#     pass
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


def receive_boards(sock):
    while True:
        print("hello")
        data = pickle.loads(sock.recvfrom(MEMORY_SIZE)[0])
        if data != b'':
            for row in data:
                for element in row:
                    print(element, end=" ")
                print()
            print()
            print("update")


# Game logic goes here


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind((MY_IP, MY_PORT))
    # Server configuration
    host = '0.0.0.0'
    port = 12345
    backlog = 1  # Maximum number of queued connections

    t1 = threading.Thread(target=receive_boards, args=(my_socket, ))
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
        for client in clients:
            if not client.is_alive():
                clients.remove(client)

        client_socket, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        clients.append(client_thread)
        client_thread.start()

    start_game.set()

    # # Start handling clients only after all players are connected
    # client_threads = []
    # for client_socket, address in connected_clients:
    #     client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
    #     client_threads.append(client_thread)
    #     client_thread.start()

    # Wait for all client threads to complete
    for client in clients:
        client.join()

    # Close the server socket
    server_socket.close()


if __name__ == "__main__":
    main()
