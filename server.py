import socket
import os
from pathlib import Path
import select 
import struct
from utils import utils as utils
from encoders.pack_response import send_packet_status, error_response


# The content-length for every request/response will be designated 4bytes for every packet
HEADER = 4
FORMAT = "utf-8"

# Types of requests/repsonse protocols between client and server
ACK_REQ = "Acknowledge"
PACKET_REQ = "Packet"


def create_server(port: int) -> None:
    """Creating a socket server that uses an IPV4 address family"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Due to compatibility issues, the default will be 127.0.0.1, feel free to change as you see fit
    # HOST = socket.gethostbyname(socket.gethostname())
    HOST = "127.0.0.1"
    ADDR = (HOST, port)

    s.bind(ADDR)
    s.listen(0)

    print(f"server has been created, listening @ {ADDR}")
    while True:
        read_conns, _, _ = select.select([s], [], [], 0)
        # if there are connections ready that we can read from 
        if read_conns:
            for conns in read_conns:
                client, addr = conns.accept()
                print(f"[new-client] -> connected from: {addr}")
                try:
                    handle_conn(client)
                except socket.error as e:
                    print(f"An error occured in socket operation: {e}")
                finally:
                    client.close()


def recv_ack_header(client: socket) -> set:
    # TODO: Add a header that allow for streaming multiple files for a single client.
    """
    This function checks the first request made my the client if it is an Ack Request, extracts information 
    and is returned to decode_packet function

    Anytime a new client connects, they must send an Ack Request. Otherwise, they must be dropped.
    The first Ack Request sent contains:
    - The number of packets that the client will send, 
    - The Working folder they are sending from, 
    - The first file they are sending
    - And their Sync-Number ie where they want to start counting at, this is to mainly make sure that 
        both client and server are in sync

    This is the only text-based protocol and so is the response. 
    The server must Acknowledge this initial request and send back an Ack Reponse with the following structure:
    Type: Acknowledge \r\n
    Status: Acknowledged \r\n
    """

    # packet = content_len + req_type + working_dir + author + client_start
    content_len = b''
    while len(content_len) < HEADER:
        chunk = client.recv(HEADER - len(content_len))
        content_len += chunk

    # we read the first 4bytes of the request, which is the Content-Length of the total payload
    # The byte is orderd is BigEndian, and then we can read the decoded amount of bytes to compelete the Ack Stage
    content_len = struct.unpack("!I", content_len)[0]
    print(f"Content-Length of Ack-Request: {content_len}") 

    payload = b''
    while len(payload) < content_len:
        chunk = client.recv(content_len - len(payload))
        payload += chunk

    print("\n === decoding header ==== \n")

    decoded_payload = payload.decode(FORMAT)
    # Since only the Ack-Request is text-based seperated by \r\n for each field
    # Using split() returns an array for each field
    body = decoded_payload.split()
    print(f"full decoded body: \n {body}")

    if body[0] != ACK_REQ:
        res_type = "Acknowledge \r\n"
        res_status = "Failed \r\n"
        encoded_res = res_type + res_status
        client.sendall(encoded_res)
        client.close()
        print("client request was not an Ack-Response, sent failed status")
        return

    print(f"Request-Type: {body[0]}")
    print(f"Expected-Packets: {body[1]}")
    print(f"Working-Dir: {body[2]}")
    print(f"Author: {body[3]}")
    print(f"Client-Sync: {body[4]}")

    print()

    # ===== Sending ACK Reponse back to Client ===== #
    res_type = "Acknowledge \r\n".encode(FORMAT)
    res_status = "Acknowledged \r\n".encode(FORMAT)

    encoded_res = res_type + res_status
    client.sendall(encoded_res)

    print("\n === sent successful acknowledged response ==== \n")

    n_packets = body[1]
    cwd = body[2]
    author = body[3]

    return (n_packets, cwd, author)


def decode_packet(client: socket, cwd: str, author: str) -> int:
    """
    This is the main decoding logic for Data-Packets. Here is the packet structure:

    ===================================================
            Content-Length: 4 bytes, BigEndian
            Request-Type-Len: 1 byte 
            Request-Type : encoded-byte-data
            Packets-Sent-Len: 4bytes, BigEndian
            Packets-Sent: encoded-byte-data
            Tag-Len: 4bytes, BigEndian
            Tag: 4bytes, BigEndian
            Data: encoded-byte-data
    ===================================================

    Theres always an offset increase based on where the current slicing position you are at.
    You should be careful editing this unless you want to go bald early

    Calls:
        - utils.find_parent()
        - utils.create_nested()

    Callers:
        - handle_conn()


    Returns:
        - Tag number of packet if IO Operation was successfull 
        - -1 if unsuccessfull 
    """

    content_len = b''
    while len(content_len) < HEADER:
        chunk = client.recv(HEADER - len(content_len))
        content_len += chunk

    content_len = struct.unpack("!I", content_len)[0]

    payload = b''
    while len(payload) < content_len:
        chunk = client.recv(content_len - len(payload))
        payload += chunk

    print("\n === full packet loaded, decoding === \n")
    offset = 0
    req_type_len = struct.unpack("B", payload[:1])[0]

    # we are currently on the second byte, since we read 1st byte ->  [0, 1, 2 ... nth]
    offset += 1
    req_type = payload[offset: offset + req_type_len].decode(FORMAT)
    # we might also check the type of request sent and validate against it
    print(f"Request-Type: {req_type}")
    offset += req_type_len

    sent_packets_len = struct.unpack("!I", payload[offset: offset + 4])[0]
    offset += 4

    sent_packets = payload[offset: offset + sent_packets_len].decode(FORMAT)
    print(f"Client-Sent: {sent_packets}")
    offset += sent_packets_len

    tag_len = struct.unpack("!I", payload[offset: offset + 4])[0]
    offset += 4

    tag = payload[offset: offset + tag_len].decode(FORMAT)
    print(f"Current tag for packet: {tag}")
    offset += tag_len

    data = payload[offset:].decode(FORMAT)
    print(data)
    print("\n\n\n")

    # print(f"Extracted-Data: {data}")
    print(f"Current-Working-Dir, CWD: {cwd}")

    print("transferring data ")

    full_path = None

    # If the author of the file in the current packet is in a nested folder, 
    # we can get it's parents and create them accordingly before any IO operation
    if "/" in author:
        nested_folders, file = utils.find_parent(author)
        full_path = utils.create_nested(cwd, nested_folders, file)
    else:
        full_path = Path.cwd() / cwd / author
        print("Writing to ", full_path)

    try:
        if (full_path is None):
            print("Why is full path still none:", full_path)
            print(type(full_path))
            return -1

        with full_path.open("a") as f:
            f.write(data)
        print(f"Data written to {full_path}")
        print("==============================================")
        print(data)
        print("==============================================")
    except Exception as e:
        print("An error occured", repr(e))
        return -1
    return int(tag)


def handle_conn(client: socket) -> None:
    """
    All operations on the client are done here.
    It first recieves the Ack Request from the client as the first Request, it closes the connection otherwise. 

    It then creates a directory of where the client is connecting from. This is gotten from the Ack-Request Header 
    and then sends an Ack-Response. 

    After the Ack-Stage, all Packets-Request sent from the clients are acknowledged with a Packet-Response.

    Calls:
        - recv_ack_header()
        - os.makedirs()
        - decode_packet()
        - send_packet_status()

    Callers: 
        - create_server()
    """
    details = recv_ack_header(client)
    if details is None:
        print("Client has already been closed, due to invalid Ack-Request")
        return

    n_packets = int(details[0])
    cwd = details[1]
    author = details[2]

    print(f"Creating client's cwd, {cwd},  on local-machine")

    try:
        os.makedirs(cwd, exist_ok=True)
    except Exception as e:
        print(f"An error occured in making cwd: {e}")
        client.send(error_response(e))
        return

    print("cwd made successfully, reading packets now...")

    packet_sync = 0
    # This is to tell the client how many packets we have received all together.
    # You can decode this on the client to see it.
    recvd = 1
    while packet_sync < int(n_packets):
        tag = decode_packet(client, cwd, author)
        if tag == n_packets:
            print("We should end the connection to the client, now", tag, n_packets)
            print("Tell the client we are about to end the connection before closing")
            client.close()

        response = send_packet_status(tag, recvd)
        recvd += 1
        print("\n -- sending success response --- \n")
        print(response)

        client.sendall(response)
        print("server-sync -> (packet_sync, recvd, tag)", (packet_sync, recvd, tag))
        packet_sync += 1


create_server(6000)
