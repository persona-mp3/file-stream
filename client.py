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
PANIC_REQ = "Panic \r\n"

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


# test_ack_res()


def streamer(file_name: str) -> None:
    s = create_client(ADDR)
    req_type = DATA_PACKET
    req_len = struct.pack("B", len(req_type))

    file = file_handler(file_name, "rb")
    packet_sync = 0

    CHUNK_SIZE = 1024
    chunks = []

    while True:
        chunk = file.read(CHUNK_SIZE)
        if not chunk:
            print("EOF file reached, nothing more to read")
            file.close()
            break

        chunks.append(chunk)

    # represents the number of packets the server should expect
    file.close()
    N_PACKETS = len(chunks)
    print(f"Total packets to send to server: {N_PACKETS}")

    print("\n === Waiting to get Acked === \n")
    is_acked = get_acked(s, N_PACKETS, file_name)
    if not is_acked:
        s.close()
        exit()

    print("\n === preparing packets to send === \n")

    while packet_sync < N_PACKETS:
        tag = str(packet_sync).encode(FORMAT)
        sent = str(packet_sync).encode(FORMAT)

        enc_tag_len = struct.pack("!I", len(tag))
        enc_sent_len = struct.pack("!I", len(sent))

        payload = req_len + req_type + enc_sent_len + sent + enc_tag_len + tag + chunks[packet_sync]
        header = struct.pack("!I", len(payload))

        packet = header + payload
        s.sendall(packet)

        packet_sync += 1

    print(" === All packets sent, closing connection ===")
    s.close()


def read_args() -> None:
    """
    Accepts Commnadline argumnets as the files to streamed over to the server
    If any file does not exists we Abort/Panic
    """
    args = sys.argv
    if len(args) < 2:
        print("fatal: not enough arguments passed in")
        exit()

    files = args[1:]

    for file in files:
        if not os.path.exists(file):
            print("fatal: this file does not exist")
            exit()
        else:
            print("streaming: ", file)
            streamer(file)


read_args()
