import socket 
import struct 
# import time 
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

    ack_header = Type.encode(FORMAT)
    encoded_n_packets = N_PACKETS.encode(FORMAT)

    body = ack_header + encoded_n_packets + Author + Start
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


def stream_file(fname: str) -> None:
    s = create_client(ADDR)
    file = file_handler(fname)
    content = file.readlines()

    codec_author = fname.encode(FORMAT)
    codec_content = [line.encode(FORMAT) for line in content]
    N_PACKETS = len(codec_content)
    print("total-packets to send: ", N_PACKETS)

    # if the server did not send an Acknowledged status we abort the mission for now
    status = send_ack(s, N_PACKETS, codec_author)
    if not status:
        exit()

    packet_sync = 0
    enc_type = struct.pack("B", len(TYPE_DATA_TRANS))
    while packet_sync < N_PACKETS:
        body = enc_type + TYPE_DATA_TRANS + codec_content[packet_sync]
        header = struct.pack("!I", len(body))

        packet = header + body
        # time.sleep(0.5)
        s.sendall(packet)

        packet_sync += 1
        # print(f"packet-sync: {packet_sync} -> {codec_content[packet_sync]}")

    print("done")
    s.close()


# stream_file("BinarySearch.java")

def stream_file2(fname: str) -> None:

    pass
