import socket
import select
import struct
import threading 
import os


from v2.logger.logger import create_logger
from v2.responses import response as res
from v2.protocol import decoder as dec
from v2.constants.constants import (
    HEADER, FORMAT,
    HOST, PORT, VERSIONS, SUPPORTED_REQ_RES, 
    ENC_PACKET_REQ_LEN, ENC_PACKET_REQ
)

ADDR = (HOST, PORT)

logger = create_logger()

# =================  declaring responses to avoid recalling them ================
unsupported_res = res.unsupported_response()
corrupted_res = res.corrupted_response()
malformed_res = res.malformed_response()
# =================================


MAX_PAYLOAD = 2 << 10


def create_server() -> socket.socket:
    """
    Creates a server-based socket, with an IPV4 Address and is ready to listen 
    for incoming clients

    Raises an Exception when an unexpected error occured, returns connected 
    socket otherwise

    Returns:
        Connected socket to the server
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(ADDR)
        s.listen(0)
        print(f"server successfully created, at {ADDR}")
        print("\n===============================")
        logger.info(f"server successfully created, at {ADDR}")
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
            # setting to None blocks until a client mainly for performace
            # setting select.select(_, _, _, timeout) to 0 will continue checking infinitely
            ready_conns, _, _ = select.select([s], [], [], None)  
            if ready_conns:
                for conn in ready_conns:
                    client, addr = conn.accept()
                    logger.info(f"New connection accepted from: {addr}")
                    print(f"New connection accepted from: {addr}")

                    # using multithreading to spin up new threads per client,as .accept() is blocking
                    thread = threading.Thread(target=handle_client, args=(client, ))
                    thread.start()
                    print(f"active-connections: {threading.active_count() - 1}")
    except Exception as err:
        logger.warn(f"Unexpected error occured: {err}")


def handle_client(client: socket.socket) -> None:
    """
    Performs the Ack-Stage for each and every client, if successfull, the protcol 
    begins.

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
        print("Content-length from client:", content_len)

        request = b''
        while len(request) < content_len:
            chunk = client.recv(content_len - len(request))
            request += chunk

        request = request.decode(FORMAT)
        request = [field for field in request.split(" \r\n") if field.strip()]
        print(f"Clients ack-request:\n {request}")

        if request[0] not in VERSIONS or request[1] not in SUPPORTED_REQ_RES:
            print("Unsupported version or request, sending unsupported response", request[0], request[1])
            # The only reason a client will not be Acknowledged is if they provide unsupported versions or requests types
            # Rather than sending an Unsupported Response, it's better to keep the protocol strict as the client will always 
            # expect an Ack-Response for an Ack-Request. 
            response = res.ack_response(False)
            client.sendall(response)
            return 
        elif len(request) < 4:
            response = res.ack_response(False)
            client.sendall(response)
            return

        response = res.ack_response(True)
        # now we can save the sessionId inside the log file and .id file in the cwd sent
        # We will only save the sessionId if any Operational Errors occur
        logger.info(f"sessionId: {response[1]}")
        client.sendall(response[0])

    # ========= Creating base directory to keep client data =========== 
        session_id = response[1]
        n_packets = request[2]
        client_cwd = request[3]
        author = request[4]

        os.makedirs(client_cwd, mode=0o777, exist_ok=True)

        start_protocol(client, session_id, client_cwd, author, n_packets)

    except Exception as err:
        print("Unexpected error: \n", err)


def start_protocol(client: socket.socket, session_id: str, cwd: str, author: str, n_packets: str) -> any:
    """
    Responsible for decoding data sent by clients and writing them to file

    Callers:
        ```handle_client()```
    """
    print("Starting protocol...")
    # Get payload from client
    content_len = b''
    while len(content_len) < HEADER:
        chunk = client.recv(HEADER - len(content_len))
        content_len += chunk

    content_len = struct.unpack("!I", content_len)[0]
    if content_len > MAX_PAYLOAD:
        logger.warn(f"Client is sending too much data of size: {content_len}, drop connection")
        # TODO: create a too-large response, but this should be also be implemented on the client instead
        client.close()
        return

    logger.info("Extracting payload")
    payload = b''
    while len(payload) < content_len:
        chunk = client.recv(content_len - len(payload))
        payload += chunk

    try:
        # decoder() -> (version, request_type, sent_packets, packet_tag, data) all in str
        # for now we'll only use the sent-packets, packet-tag and data as checksum validation is handled 
        # by decoder()
        _, _, sent_packets, packet_tag, data = dec.decoder(payload)

        # ========= Write data to file and send Packet-status response to client ====== 
        packet_status = res.packet_stats2(int(packet_tag), 20, False)
        print("sending successfull packet-status")
        client.sendall(packet_status)

    except dec.UnsupportedError:
        client.sendall(unsupported_res)
        print("closing connection due to unsupported response")
        client.close()

    except dec.CorruptionError:
        client.sendall(corrupted_res)
        print("closing connection due to corrupted data")
        client.close()

    except dec.DecoderError:
        client.sendall(malformed_res)
        print("closing connection due to decoder error")
        # client.close()


def main() -> None:
    try:
        s = create_server()
        accept_clients(s)
    except KeyboardInterrupt:
        print("Quiting server...")
    except Exception as e:
        logger.warning(e)
        print(e)


if __name__ == "__main__":
    main()
