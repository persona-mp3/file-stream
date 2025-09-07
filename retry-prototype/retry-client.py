import struct
import socket
import threading
import sys
import os
from pathlib import Path


from v2.utils import utils as utils
from v2.protocol import encoder as enc
from v2.protocol import packet_status as ps
from v2.requests import request as req
from v2.logger.logger import create_logger
from v2.constants.constants import (
    HEADER, FORMAT, VERSIONS, PORT, HOST, SUPPORTED_REQ_RES, CLOSE_CONNECTION, ACK_S, RETRY_CODE
)

ADDR = (HOST, PORT)

logger = create_logger()

# =========== Commonn Requests sent ==============
DISCONN = req.disconnect_request()
# ================================================


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
        s.connect(ADDR)
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
    request = req.ack_reconnect("new-uuid-session", "main.go", "wsl-prt", "file-cksum", "data-cksum", "12", "20")

    s.sendall(request)

    content_len = b''
    while len(content_len) < HEADER:
        chunk = s.recv(HEADER - len(content_len))
        content_len += chunk

    print("wating for reconnection-protcol")
    try: 
        content_len = struct.unpack("!I", content_len)[0]

        response = b''
        while len(response) < content_len:
            chunk = s.recv(content_len - len(response))
            response += chunk

        response = response.decode(FORMAT)
        response = [field for field in response.split(" \r\n") if field.strip()]

        if response[0] not in VERSIONS:
            logger.warning(f"Unknown version from server: {response[0]}")
            print("Server sent an invalid version: ", response[0])
            s.close()
        elif response[1] not in SUPPORTED_REQ_RES:
            logger.warning(f"Unknown reponse from server: {response[1]}")
            print(f"Server sent an unknown response-type: {response[1]}")
            s.close()

        if response[2] != ACK_S:
            print("Server invalidated out request")
            return (not is_acked, "")

        #
        # version: response[0]
        # response: response[1]
        # status: response[2]
        # session_id: response[3]
        #
        session_id = response[3]

        with open(".ssid", "w") as f:
            f.write(f"{session_id}\n")

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

    enc_data = utils.reader(file_name)

    # ========= encode data ==========
    N_PACKETS = len(enc_data)
    author = file_name

    # ========== get acked ===========
    ack_status = get_acked(s, N_PACKETS, author)
    is_acked = ack_status[0]
    if not is_acked:
        print("fatal: could not get acked by server", is_acked)
        return

    sent_packets = 1
    sync = 0

    while sync < len(enc_data):
        packet_req = enc.encoder(sync, sent_packets, enc_data[sync])
        s.sendall(packet_req)

        # wait on servers response
        try:
            response = utils.recv_payload(s)
            status_code, payload = ps.controller(response)
            if status_code in CLOSE_CONNECTION and len(payload) == 0:
                s.close()
                break
            elif status_code == RETRY_CODE:
                print("Retrial requested", status_code, payload)
                s.sendall(packet_req)
            elif status_code == ACK_S:
                sync += 1
                sent_packets += 1
                continue

        except utils.MaxPayload:
            print("Server tried to send too much data. Closing connection")

    # once this request has been recieved by the server, they should close the connection instead 
    # As if we close the connection first, the server might be left hanging 
    s.sendall(DISCONN)


def main() -> None:
    man = """ 
    Usage: 
    Send all files in current directory except .git files 
                ren .

    Send specific files that exists in current directory. If file does not exists, it simply skips it
                ren foo.txt bar.txt main.go
    Sends foo.txt, bar.txt and main.go
    """
    try:
        if len(sys.argv) < 2:
            print("fatal: no arguments passed in")
            print(man)
            exit(1)

        if sys.argv[1] == ".":
            print("Sending all files")
            files: list[str] = utils.get_all_files()
            for file in files:
                print("streaming", file)

                thread = threading.Thread(target=streamer, args=(file, ))
                thread.start()
                # streamer(file)
        elif sys.argv[1] != "." and len(sys.argv) > 1:
            for file in sys.argv[1:]:
                if os.path.exists(file):
                    streamer(file)
                else:
                    print(f"fatal: {file} does not exist")
        else:
            print("fatal: invalid arguments passed")
            print(man)
            exit(1)

    except KeyboardInterrupt:
        logger.info("Closing connection due to SIGINT")
        print("Closing connection")
        exit(0)
    except Exception as e:
        logger.warning(e)
        exit(1)


if __name__ == "__main__":
    print("running client")
    main()
