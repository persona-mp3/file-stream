import struct
import socket
import sys
from pathlib import Path


from v2.protocol import encoder as enc
from v2.protocol import packet_status as ps
from v2.requests import request as req
from v2.logger.logger import create_logger
from v2.constants.constants import (
    HEADER, FORMAT, VERSIONS, PORT, HOST,
    SUPPORTED_REQ_RES, CLOSE_CONNECTION,
    ACK_S, ENC_PACKET_REQ_LEN, ENC_PACKET_REQ
)

ADDR = (HOST, PORT)

logger = create_logger()


def create_client() -> socket.socket:
    """
    Creates a client-based socket, with an IPV4 Address and is connected 
    to the servers address and port

    Raises an Exception when an unexpected error occured, returns connected 
    socket otherwise

    Returns:
        Connected socket to the server
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # s.create_connection(ADDR, timeout=6)
        # s.settimeout(None)
        s.connect(ADDR)
        print(f"Client socket created successfully, connected at {ADDR}")
        logger.info(f"Client socket created successfully, connected at {ADDR}")
        return s
    except Exception as err:
        print(err)
        logger.critical(f"Error occured trying to create client, {err}")
        exit(1)


def get_acked(s: socket.socket, n_packets: int, file_name: str) -> tuple[bool, str]:
    """Sends an Ack-Request for a file to be sent to the server. 
    If successfull, the session id by the serve is alsp included in the return value

    Returns:
        (is_acked, session_id?)
    """
    is_acked = True
    CWD = f"{Path.cwd().name}"
    request = req.ack_request(file_name, CWD, n_packets)
    print("request to send->", request)

    s.sendall(request)

    content_len = b''
    while len(content_len) < HEADER:
        chunk = s.recv(HEADER - len(content_len))
        content_len += chunk

    try: 
        content_len = struct.unpack("!I", content_len)[0]
        print("Content-length of ack-response:", content_len)
        print("Extracting response")

        response = b''
        while len(response) < content_len:
            chunk = s.recv(content_len - len(response))
            response += chunk

        response = response.decode(FORMAT)
        response = [field for field in response.split(" \r\n") if field.strip()]
        print("Response fields -> ", response)

        if response[0] not in VERSIONS:
            logger.warning(f"Unknown version from server: {response[0]}")
            print("Server sent an invalid version: ", response[0])
        elif response[1] not in SUPPORTED_REQ_RES:
            logger.warning(f"Unknown reponse from server: {response[1]}")
            print(f"Server sent an unknown response-type: {response[1]}")

        print("Valid response from server")
        if response[2] != ACK_S:
            print("Server invalidated out request")
            return (not is_acked, "")

        print("Full Response Details\n")
        print(f"Version -> {response[0]}")
        print(f"Response -> {response[1]}")
        print(f"Status -> {response[2]}")
        print(f"SessionId-> {response[3]}")
        print("Begin protcol with server")
        session_id = response[3]
        return (is_acked, session_id)

    except struct.error as err:
        print("An error occcured trying to read ack-response from server:\n", err, "\n")


def streamer(file_name: str) -> None:
    """
    Calls:
        create_client()
        get_acked()
        enc.encoder()
    """
    s = create_client()

    if not isinstance(file_name, str):
        raise ValueError("Expected type of str, got", type(file_name))
        return

    # ========== test data =========
    data = "The Joe Roegan Experience #225".encode(FORMAT)
    tag = 10 
    sent = 10 
    author = "main.go"
    n_packets = 12

    ack_status = get_acked(s, n_packets, author)

    # ========== get acked ===========
    is_acked = ack_status[0]
    if not is_acked:
        print("fatal: could not get acked by server", is_acked)
        return

    # ========= encode data ==========
    req = enc.encoder(tag, sent, data)
    s.sendall(req)

    # ======= wait for response ==== 
    content_len = b''
    while len(content_len) < HEADER:
        chunk = s.recv(HEADER - len(content_len))
        content_len += chunk

    content_len = struct.unpack("!I", content_len)[0]

    response = b''
    while len(response) < content_len:
        chunk = s.recv(content_len - len(response))
        response += chunk

    # getting information on the type of response sent by server:
    status_code, payload = ps.controller(response)
    print("total-response", response)
    print(f"status-code:{status_code}\npayload: {payload}")
    if status_code in CLOSE_CONNECTION and len(payload) == 0:
        logger.warning(f"Closing connection with server due to: {status_code}")
        s.close()


def main() -> None:
    try:
        if len(sys.argv) < 2:
            print("fatal: no arguments passed in")
            exit(1)

        if sys.argv[1] == ".":
            print("Sending all files")
            streamer("mock")
    except KeyboardInterrupt:
        logger.info("Closing connection due to SIGINT")
        print("Closing connection")
        exit(0)


if __name__ == "__main__":
    main()
