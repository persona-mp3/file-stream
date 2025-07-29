import struct 
import socket
import os
import sys
from utils.utils import file_handler, create_client
from encoders.pack_response import verify_packet_status
from utils import utils as utils

FORMAT = "utf-8"

HOST = "127.0.0.1"
PORT = 6000
ADDR = (HOST, PORT)

HEADER = 4

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
    """
    Takes a file, uses utils functions from the Utils module, and creates packets from the file and streams over to 
    the TCP Server. This protocol is byte-based, so alot of encoding and offsetting will be done on the server-side, it's 
    important to be careful here. 

    body = req_len + req_type + enc_sent_len + sent + enc_tag_len + tag + data
    packet = len(body) + body

    Content-Length/ Header = 4bytes, BigEndian
    Encoded-Sent-Length, Sent, Encoded-Tag-Length, Tag = 4bytes, BigEndian

    The Sent and Tag fields are used to communicate to the server, how many packets have been sent to the them, 
    the client needs to confirm this in before sending Packet-Status Response. Anything aside 200 will stop the normal flow.

    Calls:
        - utils.create_client()
        - utils.file_handler()
        - get_acked()
        - encoders.pack_response.verify_packet_status()

    """
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
        tag = str((packet_sync + 1)).encode(FORMAT)
        sent = str((packet_sync + 1)).encode(FORMAT)

        enc_tag_len = struct.pack("!I", len(tag))
        enc_sent_len = struct.pack("!I", len(sent))

        # time.sleep(2)

        payload = req_len + req_type + enc_sent_len + sent + enc_tag_len + tag + chunks[packet_sync]
        print(f"Current Chunk to send: \n {chunks[packet_sync].decode(FORMAT)} \n\n\n\n")
        header = struct.pack("!I", len(payload))

        packet = header + payload
        s.sendall(packet)

        print("\n == waiting on packet status from encoder.verify_packet_status() == \n")

        # TODO: Explicit packet reading
        server_response = s.recv(1024)
        ok = verify_packet_status(server_response)
        if not ok:
            print("ERRORRRRR")
            print(server_response[4:])
            print("resend this packet then")
            continue

        print(f"server response: \n {server_response[4:]}")
        print("packet-sync:", packet_sync)

        packet_sync += 1

    print(" === All packets sent, closing connection ===")
    s.close()


def main() -> None:
    """
    Reads arguments from commandline on files to stream

    Calls:
        - sys.argv
        - os.path.exists()
        - streamer
        - utils.get_all_files()

    Callers:
        None


    """
    if len(sys.argv) < 2:
        print("fatal: not enought arguments found")
        return

    if sys.argv[1] == ".":
        print("Sending whole directory to the server...")
        # time.sleep(1.1)
        files = utils.get_all_files()
        for file in files:
            print("Streaming: ", file)
            streamer(file)
    elif sys.argv[1] != "." and len(sys.argv) > 2:
        print("Streaming single files...")
        # time.sleep(1.1)

        for file in sys.argv[1:]: 
            if os.path.exists(file):
                streamer(file)
            else:
                print(f"Abort: file, {file} does not exist")
                exit()
    else:
        print("fatal: invalid argument passed in")
        print("use python3 client.py . to send all files to server")
        print("use python3 client.py f1, f2 ... to send individual files to server")
        exit()


main()
