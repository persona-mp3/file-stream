import struct 
import socket
import os
import sys
from utils.utils import file_handler, create_client

FORMAT = "utf-8"

HOST = "127.0.0.1"
PORT = 6000
ADDR = (HOST, PORT)

ACK_REQ = "Acknowledge \r\n"
ACK_RES = "Acknowledged"
DATA_PACKET = "Packet".encode("utf-8")


def get_acked(s: socket, packets: int, file_name: str) -> bool:
    """
    This function sends an Ack-Request to the Server, using a text based protocol. 
    It also waits for the server to Acknowledge the request.
    If successful, function returns True otherwise False
    """
    is_acked = True

    req_type = ACK_REQ.encode(FORMAT)
    n_packets = (str(packets) + " \r\n").encode(FORMAT)
    author = (file_name + " \r\n").encode(FORMAT)
    start = "0 \r\n".encode(FORMAT)
    CWD = (os.path.basename(os.getcwd()) + " \r\n").encode(FORMAT)

    content = req_type + n_packets + CWD + author + start
    content_len = struct.pack("!I", len(content))

    packet = content_len + content
    s.sendall(packet)

    print("\n === packet sent, awaiting acknowledgement response === \n")

    # Ack-Response will always be 29 bytes, unless it should be considered as Failed Acknowledgement
    ACK_RES_LEN = 29
    response = s.recv(ACK_RES_LEN).decode(FORMAT)
    acked = response.split()[1]

    if acked != ACK_RES:
        print(f"Server did not acknowledge out request. Sent status of: {acked}")
        return not is_acked

    print("Server acknowledged our request, continue protocol")
    return is_acked


def test_ack_res():
    s = create_client(ADDR)
    n_packets = 50
    author = "Himalays.js"

    is_acked = get_acked(s, n_packets, author)
    if not is_acked:
        exit()

    print("We got acknowledged!")
    return 


test_ack_res()
