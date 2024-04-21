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
    print("welcome player!")
    player_code = generate_unique_id(addr[0], addr[1]).encode()
    sent = 0
    try:
        # send message length
        while sent < len(player_code):
            sent += sock.send(player_code[sent:])
    except socket.error as err:
        pass
    # Game logic goes here


def main():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind((MY_IP, MY_PORT))
    # Server configuration
    host = '0.0.0.0'
    port = 12345
    backlog = 1  # Maximum number of queued connections

    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the host and port
    server_socket.bind((host, port))

    # Start listening for incoming connections
    server_socket.listen(backlog)
    print(f"Server listening on {host}:{port}")

    connected_clients = []

    # Accept connections
    while len(connected_clients) < backlog:
        client_socket, address = server_socket.accept()
        connected_clients.append((client_socket, address))
        print(f"Accepted connection from {address}")

    # Start handling clients only after all players are connected
    client_threads = []
    for client_socket, address in connected_clients:
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_threads.append(client_thread)
        client_thread.start()

    # Wait for all client threads to complete
    for client_thread in client_threads:
        client_thread.join()

    # Close the server socket
    server_socket.close()




# def main2():
#     clients_to_send = []  # made up from ((ip, port), board)
#
#     my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     my_socket.bind((MY_IP, MY_PORT))
#     pygame.init()
#     screen = pygame.display.set_mode(WINDOW_SIZE)
#     pygame.display.set_caption("Server")
#     clock = pygame.time.Clock()
#     # Initialize board and state
#     board = Board()
#     state = State(board)
#
#     # draw the screen
#     screen.fill(WHITE)
#     draw_boards(screen, board)
#
#     for i in range(4):
#         draw_other_player(screen, board, i)
#
#     pygame.display.flip()
#
#     game_over = False
#
#     send_interval = 1 / 60
#     send_thread = threading.Thread(target=send_states, args=(send_interval, my_socket, clients_to_send))
#     send_thread.start()
#
#     while not game_over:
#         received = recv_data(my_socket)
#         if received:
#             board = received[0]
#             game_over = received[1]
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 game_over = True
#
#         for i, opp in enumerate(clients_to_send):
#             draw_other_player(screen, opp[1], i)
#
#         screen.fill(WHITE)
#         draw_boards(screen, board)
#         pygame.display.flip()
#
#         # game_over = state.game_over
#
#     # time.sleep(3)
#     # for row in reversed(state.board.board):
#     #     for element in row:
#     #         print(element, end=" ")
#     #     print()
#     # print()
#     send_thread.join()
#     pygame.quit()


if __name__ == "__main__":
    main()
