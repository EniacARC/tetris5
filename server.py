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

MY_IP = "0.0.0.0"
UDP_PORT = 7372
TCP_PORT = 12345
BACKLOG = 5  # Maximum number of queued connections and the number of clients

# msgs
CONNECTION_PATTERN = r"^LISTEN ON (\d+)"

start_game = threading.Event()
end_game = threading.Event()

MEMORY_SIZE = (4 * 3) * 10 * 20
ID_SIZE = 256

# boards_lock = threading.Lock()
addr_lock = threading.Lock()
addresses = {}
lines_to_send = {}




def generate_unique_id(ip, port):
    """
    Generate a unique identifier based on the combination of IP address and port.

    :param ip: The IP address.
    :type ip: str
    :param port: The port number.
    :type port: int

    :return: A unique identifier.
    :rtype: str
    """
    # Concatenate IP address and port as a string
    combined_str = f"{ip}:{port}"

    # Hash the combined string using SHA-256 (you can choose a different hash function if needed)
    hashed = hashlib.sha256(combined_str.encode()).hexdigest()

    return hashed


def handle_client(sock, addr):
    """
    Handle communication with a client.

    :param sock: The socket for communication with the client.
    :type sock: socket.socket
    :param addr: The address of the client.
    :type addr: tuple (str, int)

    :return: None
    """
    global addresses
    global lines_to_send

    try:
        # start initial connection,
        a = receive_tcp(sock).decode()
        if re.search(CONNECTION_PATTERN, a) is None:
            return

        # save address and create id form it
        player_address = (addr[0], int(''.join(filter(str.isdigit, a))))
        player_id = generate_unique_id(addr[0], addr[1])

        with addr_lock:
            #
            addresses[player_address] = player_id
            lines_to_send[player_id] = 0

        while not start_game.is_set():
            send_tcp(sock, "READY".encode())
            if receive_tcp(sock).decode() != "READY":
                return

        send_tcp(sock, "START".encode())

        lines_to_add = 0
        game_over = False

        while not game_over:
            lines = 0
            with addr_lock:
                if lines_to_send[player_id] != 0:
                    lines = lines_to_send[player_id]
                    lines_to_send[player_id] = 0

            if lines != 0:
                threading.Thread(target=send_tcp,
                                 args=(sock, struct.pack(PACK_SIGN, socket.htonl(lines)))).start()
            a = receive_tcp(sock)

            if a != b'':
                a = a.split(b'|')
                lines_to_add = socket.htonl(struct.unpack(PACK_SIGN, a[0])[0])
                with addr_lock:
                    filtered_keys = [key for key in lines_to_send.keys() if key != player_id]
                    lines_to_send[random.choice(filtered_keys)] += lines_to_add

                game_over = struct.unpack('?', a[1])[0]
            elif a == b'ERROR':
                game_over = True

        with addr_lock:
            del addresses[player_address]

    except socket.error as err:
        print(f"error: {err}")


def send_board(sock, addr, board):
    """
    Send the game board to other players.

    :param sock: The UDP socket for sending data.
    :type sock: socket.socket
    :param addr: The address of the player to send the board to.
    :type addr: tuple (str, int)
    :param board: The game board data to send.
    :type board: bytes

    :return: None
    """
    if addr in addresses.keys():
        send_id = addresses[addr]

        for s_ad, s_id in addresses.items():
            if s_ad != addr:
                try:

                    msg = send_id.encode() + board
                    sock.sendto(msg, s_ad)
                except socket.error as err:
                    print(f"error while updating player at {addresses[i]}")


def receive_boards(sock):
    """
    Receive game boards from other players.

    :param sock: The UDP socket for receiving data.
    :type sock: socket.socket

    :return: None
    """
    while not end_game.is_set():
        try:
            data, addr = recv_udp(sock, MEMORY_SIZE)
            if data != b'':
                send_board_thread = threading.Thread(target=send_board, args=(sock, addr, data))
                send_board_thread.start()

        except socket.error as err:
            pass


def main():
    """
    the main function; responsible for running the server code.
    """
    global addresses

    # define and bind udp socket
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.bind((MY_IP, UDP_PORT))
    my_socket.settimeout(1)

    # define and bind tcp socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((MY_IP, TCP_PORT))

    t1 = threading.Thread(target=receive_boards, args=(my_socket,))
    t1.start()

    # Start listening for incoming connections
    server_socket.listen(BACKLOG)
    print(f"Server listening on {MY_IP}:{TCP_PORT}")

    # wait for BACKLOG num of clients to connect for the game to start
    clients = []

    # Accept connections
    while len(clients) < BACKLOG:

        client_socket, address = server_socket.accept()
        client_socket.settimeout(1)

        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        clients.append((address, client_thread))
        client_thread.start()

        # if client was disconnected before the game starts then remove him
        for client in clients:
            if not client[1].is_alive():
                with addr_lock:
                    address = client[0]
                    if address in addresses.keys():
                        del lines_to_send[address]
                        del addresses[address]
                clients.remove(client)

    start_game.set()

    # Wait for all client threads to complete
    for client in clients:
        client[1].join()

    end_game.set()

    # Close the server socket
    server_socket.close()


if __name__ == "__main__":
    main()
