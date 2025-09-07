import socket
import select
import struct
import threading 
import os


from redis_client import validate_client
from v2.logger.logger import create_logger
from v2.constants.constants import (
    HEADER, FORMAT, HOST, PORT
)

ADDR = (HOST, PORT)

logger = create_logger()


MAX_PAYLOAD = 2 << 10


def create_server() -> socket.socket:
    """
    Returns:
        Connected socket to the server
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(ADDR)
        s.listen(0)
        logger.info(f"server successfully created, at {ADDR}")
        print("server running")
        return s
    except Exception as err:
        logger.critical(f"Error occured trying to create server, {err}")
        exit(1)


def accept_clients(s: socket.socket) -> None:
    """
    Calls: 
    ````handle_client(client: socket.socket)```
    """
    if not isinstance(s, socket.socket):
        logger.warn(f"Invalid argument passed in, expected socket, got {type(s)}")
        raise ValueError(f"Invalid argument passed in, expected socket, got {type(s)}")

    try:
        while True:
            ready_conns, _, _ = select.select([s], [], [], None)  
            if ready_conns:
                for conn in ready_conns:
                    client, addr = conn.accept()
                    logger.info(f"New connection accepted from: {addr}")
                    print("New connection:", addr)
                    # using multithreading to spin up new threads per client,as .accept() is blocking
                    thread = threading.Thread(target=handle_client, args=(client, ))
                    thread.start()
    except Exception as err:
        logger.warn(f"Unexpected error occured: {err}")


def handle_client(client: socket.socket) -> None:
    """
    Calls:
       ```start_protocol()```
    """
    if not isinstance(client, socket.socket):
        logger.warn(f"Expected socket object, got: {type(client)}")
        raise ValueError(f"Expected socket object, got: {type(client)}")

    # ========= Ack Client first =========== 
    try:
        content_len = b''
        while len(content_len) < HEADER:
            chunk = client.recv(HEADER - len(content_len))
            content_len += chunk

        content_len = struct.unpack("!I", content_len)[0]

        request = b''
        while len(request) < content_len:
            chunk = client.recv(content_len - len(request))
            request += chunk

        request = request.decode(FORMAT)
        request = [field for field in request.split(" \r\n") if field.strip()]

        print("All fields for reconnection")
        print((request))

        # use redis to verify this data
        session_id = request[2]
        author = request[3]

        session_id, author, cwd, file_cksum, packet_id, data_cksum, n_packets = request[2], request[3], request[4], request[5], request[6], request[7], request[8]
        print(f"""
              session_id -> {session_id}
              author -> {author}
              cwd -> {cwd}
              file_cksum -> {file_cksum}
              packet_id -> {packet_id}
              data_cksum -> {data_cksum}
              n_packets -> {n_packets}
              """)

        # check if the file even exists first thing 
        file_location = os.path.join(cwd, author)
        cwd_status = os.path.exists(cwd)
        file_status = os.path.exists(file_location)

        if not cwd_status and not file_status:
            print("we can continue to check redis now")
            client_data = validate_client(session_id)
            print("Redis returned:")
            print(client_data)

        else:
            print("Baloney")

    except Exception as err:
        print("Unexpected error: \n", err)


def main() -> None:
    try:
        s = create_server()
        accept_clients(s)
    except KeyboardInterrupt:
        print("Quiting server...")
        exit(0)
    except Exception as e:
        logger.warning(e)
        exit(1)


if __name__ == "__main__":
    main()
