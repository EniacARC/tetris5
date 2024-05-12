import socket
import struct

INT_SIZE = 4
PACK_SIGN = "I"


def send_tcp(sock, data):
    length = struct.pack(PACK_SIGN, socket.htonl(len(data)))
    # basic protocol - length|byte(data)
    to_send = length + data
    # print(f"sending: {to_send}")
    try:
        sent = 0
        while sent < len(to_send):
            sent += sock.send(to_send[sent:])
    except socket.error as err:
        print(f"error while sending at: {err}")


def receive_tcp(sock):
    try:
        length = 0
        buf = b''
        data_len = b''
        data = b''
        while len(data_len) < INT_SIZE:
            buf = sock.recv(INT_SIZE - len(data_len))
            if buf == b'':
                data_len = b''
                break
            data_len += buf

        if data_len != b'':
            length = socket.htonl(struct.unpack(PACK_SIGN, data_len)[0])
        while len(data) < length:
            buf = sock.recv(length - len(data))
            if buf == b'':
                data = b''
                break
            data += buf

        return data

    except socket.error as err:
        print(f"error while recv: {err}")
        return b''


def recv_udp(sock, length):
    try:
        return sock.recvfrom(length)
    except socket.timeout as timeout:
        return b'', (0, 0)
