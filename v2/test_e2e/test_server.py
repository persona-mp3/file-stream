import socket 
import struct 

from v2.constants.constants import (HEADER, FORMAT)
from v2.responses import response as res

HOST = "127.0.0.1"
PORT = 6000


def create_server() -> socket.socket:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(0)
        print("server successfully created")
        return s
    except Exception as err:
        print(f"Error occured trying to create server, {err}")
        exit(1)


def recv_ack_request(client: socket.socket) -> bool:
    # extracting content-len 
    try:
        content_len = b''
        while len(content_len) < HEADER:
            chunk = client.recv(HEADER - len(content_len))
            content_len += chunk

        content_len = struct.unpack("!I", content_len)[0]
        print("Content-length from client:", content_len)

        request = b''
        while len(request) < content_len:
            chunk = client.recv(content_len - len(request))
            request += chunk

        request = request.decode(FORMAT)
        request = [field for field in request.split(" \r\n") if field.strip()]
        print(f"Clients ack-request:\n {request}")
        response = res.ack_response(True)
        print("sessionId: {response[1]}")

        client.sendall(response[0])
    except Exception as err:
        print("Unexpected error: \n", err)
