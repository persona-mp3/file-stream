import socket 
import struct
import os 
import select 
import threading 
from typing import NamedTuple
from pathlib import Path 

# number of bytes to read for content-length
HEADER = 4
VERSION = "001"

# decoding and encoding format for binary protocol 
FORMAT = "utf-8"

ACK_REQ = "Acknowledge"
ACK_S = "200"
ACK_F = "400"

PACKET_REQ = "Packet"
PACKET_RES = "Packet-Status"

ENC_PACKET_REQ: bytes = PACKET_REQ.encode(FORMAT)

HOST = "0.0.0.0"

ENC_VERSION: bytes = (VERSION + " \r\n").encode(FORMAT)
ENC_VERSION_LEN: bytes = struct.pack("B", len(ENC_VERSION))  

ENC_ACK_REQ: bytes = (ACK_REQ + " \r\n").encode(FORMAT)
ENC_ACK_S: bytes = (ACK_S + " \r\n").encode(FORMAT)
ENC_ACK_F: bytes = (ACK_F + " \r\n").encode(FORMAT)


def create_server(port: int = 6000) -> None: 
    """ 
    Creates a TCP Socket with a default port of 6000, and IP of 0.0.0.0

    Calls:
        - socket
        - handle_conn()

    Callers:
        - None
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ADDR = (HOST, port)

    s.bind(ADDR)
    s.listen(0)

    print(f"[server created at], {ADDR}, listening for connections")

    while True:
        # select.select is a non-blocking module 
        read_conns, _, _ = select.select([s], [], [], 0)
        # if any connections are ready to be read from
        if read_conns:
            for conn in read_conns:
                client, addr = conn.accept()  # accept the client
                print(f"[new client] -> {addr} \n\n")
            try: 
                handle_conn(client)
                # To handle clients concurrently, we can use the threading module to make sure server can handle multiple clients at the "same" time
                # thread = threading.Thread(target=handle_conn, args=(client,))
                # thread.start()
            except socket.error as e:
                print(f"An error occured in socket operation: {e}")
            finally:
                client.close()


# dataclass to represent structure of "Data". Think of them as structs, objects, or even custom types 
class AckInfo(NamedTuple):
    n_packets: int
    CWD: str 
    author: str


def ack_client(client: socket.socket) -> AckInfo:
    """
    Expects an Ack-Request from the client including the following in the header:
        - Version: "001 \r\n", Request-Type: "Acknowledge \r\n", Author:fileName \r\n, N_PACKETS: 12 \r\n
    The server sends an Ack-Response in the following format:
        - Version: "001 \r\n", Request-Type: "Acknowledge \r\n", Status: "Acknowledged \r\n"

    Calls:
        - struct

    Callers: 
        - handle_conn()
    """
    if not isinstance(client, socket.socket):
        raise ValueError("Expected socket object, got: " + str(type(client)))
        return 

    content_len = b''
    while len(content_len) < HEADER:  # we are going to read the first 4 bytes sent ie HEADER of the request/packet
        chunk = client.recv(HEADER - len(content_len))
        content_len += chunk

    # decoding content_len in BigEndian
    content_len = struct.unpack("!I", content_len)[0]
    print(f"Content-length for ack-request -> {content_len}")

    payload = b''
    while len(payload) < content_len:
        chunk = client.recv(content_len - len(payload))
        payload += chunk

    print("\n\n --- decoding Ack-Request --- \n\n")
    # Since only the Ack-Request is text-based seperated by  a \r\n for each field
    payload = [field.strip() for field in payload.decode(FORMAT).split(" \r\n") if field.strip()]  # seperating all the fields and remove " "
    print(f"[ack-request] ->  {payload}")

    if (
        payload[0] != VERSION or
        payload[1] != ACK_REQ or 
        len(payload) > 5  # extra validation against invalid packet-requests
    ): 
        response: bytes = ENC_VERSION + ENC_ACK_REQ + ENC_ACK_F
        print(f"Invalid Ack-Request, sending status of {ENC_ACK_F}, and closing connection")
        print(payload[0], payload[1], len(payload))
        client.sendall(response)
        client.close()
        return

    # ===== Sending Ack-Reponse back to Client ===== #
    print(f"[valid-request] -> sending status of {ACK_S}")
    response: bytes = ENC_VERSION + ENC_ACK_REQ + ENC_ACK_S
    client.sendall(response)

    return AckInfo(20, "Reafactor", "Please-Work")


def handle_conn(client: socket.socket) -> None:
    print("handling client...")
    ack_client(client)


def main() -> None:
    create_server()


main()
