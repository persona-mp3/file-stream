import socket 
import struct
import sys
import os
import time

from pathlib import Path 
from utils import utils as utils
from protocol import encode as enc

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
    """
    Handles structuring of Ack-Request for each file sent to the server. 
    It also handles sending the CWD, but the Caller has to provide the 
    file_name and expected number of packets, n_packets.

    Callers:
        streamer() -> None

    Returns:
        - True if server Acknowledged our Request with code of 200, False otherwise
    """
    is_acked = True 

    expected_packets: bytes = (str(n_packets) + " \r\n").encode(FORMAT)
    # author: bytes = f"{file_name} \r\n".encode(FORMAT)
    author: bytes = (str(file_name) + " \r\n").encode(FORMAT)
    CWD: bytes = (str(Path.cwd().name) + " \r\n").encode(FORMAT)
    print(f"cwd of client -> {CWD}")

    payload: bytes = ENC_VERSION + ENC_ACK_REQ + expected_packets + CWD + author
    header: bytes = struct.pack("!I", len(payload))
    ack_request: bytes = header + payload

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


def read_file(file_name: str) -> list[bytes]:
    """
    Takes in a file_name, and reads it's content into a list.
    All filenames passed in must be verfied that they exist first

    Calls:
        os

    Callers:
        streamer() 

    Returns:
        List of data in bytes
    """
    try:
        # we want to read the file contents 1024bytes at a time
        CHUNK = 1024
        content: list[bytes] = []

        print(f"[reading] -> {file_name}")
        with open(file_name, "rb") as f:
            while True:
                chunk: bytes = f.read(CHUNK)
                if not chunk:
                    print("EOF reached")
                    break
                content.append(chunk)

        return content

    except Exception as e:
        print("An unexpected error occured\n ", repr(e))


def streamer(file_name: str) -> None: 
    """
    Calls:
        create_client() -> socket.socket
        get_acked() -> bool

    Callers:
        - main()
    """
    s: socket.socket = create_client()

    file_content: list[bytes] = read_file(file_name)
    N_PACKETS = len(file_content)

    is_acked: bool = get_acked(s, N_PACKETS, file_name)
    if not is_acked:
        return

    print("\n--- begining protocol ---\n")

    sync = 0 
    sent = 1
    while sync < N_PACKETS:
        enc_packet: bytes = enc.encode_packet(file_content[sync], sent, sent)  # The tag of each packet can match the number of packets sent
        s.sendall(enc_packet)

        # === Waiting on Packet-Status Response ===
        time.sleep(0.3)
        print("...waiting on packet-status")
        sync += 1
        sent += 1


def main() -> None:
    """
    Read file arguments passed in command-line

    Calls:
        os
        sys.argv -> list[str]
        utils.get_all_files() -> list[str]

    Callers:
        None

    Returns:
        None
    """
    if len(sys.argv) < 2:
        print("fatal: No file arguments passed in.")
        return

    if sys.argv[1] == ".":
        print("Sending whole directory to server...")
        # recursively gets all file paths and their sub-folders in CWD
        all_files: list[str] = utils.get_all_files()
        for file in all_files:
            streamer(file)

    elif sys.argv[1] != "." and len(sys.argv) > 1:
        for file in sys.argv[1:]:
            if os.path.exists(file):
                streamer(file)
            else:
                # tell server to abort the mission
                print(f"fatal: {file} does not exist, aborting proccess")
                exit()
    else:
        print("fatal: Invalid arguments passed in \n \n ren . -> Sends all files in CWD \n\n ren f1 f2 ... -> sends f1 and f2 \n\n")
        exit()


main()
