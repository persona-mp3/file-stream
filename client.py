import sys
import os
import socket 
import struct 
from utils.utils import file_handler, create_client

# HOST = socket.gethostbyname(socket.gethostname())
HOST = "127.0.0.1"
PORT = 6000
ADDR = (HOST, PORT)
FORMAT = "utf-8"

# The Acknowledged response from the server will always be 29 bytes
# And will be in the format of:
# Type: Acknowledge \r\n
# Status: Acknowledged \r\n
ACKED = "Acknowledged"
ACK_REQ_BODY = 29

TYPE_DATA_TRANS = "Packet".encode(FORMAT)
ENC_DATA_TRANS = struct.pack("B", len(TYPE_DATA_TRANS))


def send_ack(s: socket, n: int, codec_author: bytes) -> bool:
    is_acknowledged = True

    Type = "Acknowledge \r\n"
    N_PACKETS = str(n) + " \r\n"
    Author = codec_author + " \r\n".encode(FORMAT)
    Start = "0".encode(FORMAT)
    CWD = (os.path.basename(os.getcwd()) + " \r\n").encode(FORMAT)

    ack_header = Type.encode(FORMAT)
    encoded_n_packets = N_PACKETS.encode(FORMAT)

    body = ack_header + encoded_n_packets + CWD + Author + Start 
    header = struct.pack("!I", len(body))

    ack_req = header + body
    print("prepared body, sending body to server")
    s.sendall(ack_req)

    response = s.recv(ACK_REQ_BODY)
    status = response.decode(FORMAT)
    response_body = status.split()[1]

    if response_body == ACKED:
        print("request acknowlegde, we can continue the protocol")
        return is_acknowledged 
    else:
        print("what did we recieve, failed responses and other things can go here")
        return not is_acknowledged


def test_ack_header():
    s = create_client(ADDR)
    N_PACKETS = 20
    codec_author = "joji".encode(FORMAT)

    status = send_ack(s, N_PACKETS, codec_author)
    if not status:
        print(f"server failed to acknowledge us for why? status : {status}")
        exit()


# test_ack_header()


def streamer(fname: str) -> None:
    print(f"streaming {fname}")
    s = create_client(ADDR)
    req_type = "Packet".encode("utf-8")
    req_len = struct.pack("B", len(req_type))

    FORMAT = "utf-8"

    file = file_handler(fname, "rb")
    packet_sync = 0 

    CHUNK_SIZE = 1024
    chunks = []
    while True:
        chunk = file.read(CHUNK_SIZE)
        if not chunk:
            print("no more content to read from file, closing file")
            file.close()
            break
        chunks.append(chunk)

    N_PACKETS = len(chunks)
    print("total packets to send:", N_PACKETS)

    status = send_ack(s, N_PACKETS, fname.encode(FORMAT))

    if not status:
        print("Server did not acknowledge request")
        s.close()
        exit()

    while packet_sync < N_PACKETS:
        tag = str(packet_sync).encode(FORMAT)
        sent = str(packet_sync).encode(FORMAT)

        enc_tag_len = struct.pack("!I", len(tag))
        enc_sent_len = struct.pack("!I", len(sent))

        body = req_len + req_type + enc_sent_len + sent + enc_tag_len + tag + chunks[packet_sync]
        header = struct.pack("!I", len(body))

        packet = header + body

        s.sendall(packet)
        packet_sync += 1

    print("all packets sent, closing socket")
    s.close()
    print("Connection closed")


def main_fn() -> None:
    """This is used to read command line arguments for files to stream"""
    args = sys.argv 
    if len(args) < 2:
        print("fatal: not enough arguments passed in")
        exit()

    files = args[1:]
    print("streaming the following files", "".join(files))

    for file in files:
        if os.path.exists(file):
            streamer(file)
        else:
            print(f"fatal: this file does not exist, {file}")
            continue

    return


main_fn()
