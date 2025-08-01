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
ENC_ACK_REQ = f"{ACK_REQ} \r\n".encode(FORMAT)

ACK_S = "200"
ACK_F = "400"

PACKET_REQ = "Packet"
PACKET_RES = "Packet-Status"

ENC_PACKET_REQ: bytes = PACKET_REQ.encode(FORMAT)

HOST = "0.0.0.0"

ENC_VERSION: bytes = (VERSION + " \r\n").encode(FORMAT)
ENC_VERSION_LEN: bytes = struct.pack("B", len(ENC_VERSION))  

ENC_ACK_S: bytes = (ACK_S + " \r\n").encode(FORMAT)

ADDR = ("0.0.0.0", 6000)


def create_client() -> socket.socket:
    """
    Connects to server's configured IP address and port. An exception is raised 
    if any errors occur

    Calls:
        - socket

    Callers:
        - main()

    Returns:
        - socket.socket connected to the server, ready for operations.

    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect(ADDR)
        print(f"Connected to server... {ADDR}")
        return s
    except Exception as e:
        print(f"An error occured in creating client: \n  {repr(e)} \n\n")


def get_acked(s: socket.socket, n_packets: int, file_name: str) -> bool:
    is_acked = True 

    expected_packets: bytes = (str(n_packets) + " \r\n").encode(FORMAT)
    # author: bytes = f"{file_name} \r\n".encode(FORMAT)
    author: bytes = (str(file_name) + " \r\n").encode(FORMAT)
    CWD: bytes = (str(Path.cwd().name) + " \r\n").encode(FORMAT)
    print(f"cwd of client -> {CWD}")

    payload = ENC_VERSION + ENC_ACK_REQ + expected_packets + CWD + author
    header = struct.pack("!I", len(payload))
    ack_request = header + payload
    s.sendall(ack_request)

    # ---- to decode the Ack-Request, a predefined length will be used to avoid unescessary overhead ---

    payload = s.recv(26)  # amount of bytes of  the Ack-Request will always be 26, otherwise invalid
    payload = [field.strip() for field in payload.decode(FORMAT).split(" \r\n") if field.strip()]  # seperating all the fields and remove " "
    print(payload)

    if (
        payload[0] != VERSION or
        payload[1] != ACK_REQ or 
        len(payload) > 3  # extra validation against invalid packet-responses
    ): 
        print("This response is invalid, so we should let the server know? Nah thats too much work atm")
        print(payload[0], payload[1], len(payload))
        return not is_acked

    if payload[2] == ACK_F:
        print("Server did not Acknowledge us, status of ", payload[2])
        return not is_acked

    if payload[2] != ACK_S:
        print("The server sent an unindentified status code of", payload[2])
        return not is_acked

    return payload[2] == ACK_S


def main() -> None: 
    """
    Calls:
        create_client() -> socket.socket
        get_acked() -> bool

    Callers:
        - None
    """
    s: socket.socket = create_client()
    is_acked = get_acked(s, 20, "Swing Lynn: Slowed Version")
    if not is_acked:
        return

    print("Continue")


main()
