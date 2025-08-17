import struct 

from ..logger.logger import create_logger
from ..constants.constants import (
    ACK_VERSION_2, VERSION_LEN, ENC_VERSION_2, 
    FORMAT, ENC_ACK_REQ,
    ENC_DISCONN_LEN, ENC_DISCONN_REQ, DISCONN_CODE
)


logger = create_logger()


def ack_request(author: str, CWD: str, n_packets=int) -> bytes:
    """
    Creates and Ack-Request ready to send to the server. 
    ```author``` is name of file 
    ```cwd``` current working directory and ```n_packets``` number of packets to send

    Returns:
        Encoded Ack-Request in bytes delimited by carraige returns for each field
    """
    enc_cwd = f"{CWD} \r\n".encode(FORMAT)
    enc_n_packets = f"{n_packets} \r\n".encode(FORMAT)
    enc_author = f"{author} \r\n".encode(FORMAT)

    payload = (ACK_VERSION_2 + ENC_ACK_REQ + enc_n_packets + enc_cwd + enc_author)
    header = struct.pack("!I", len(payload))

    request = header + payload
    return request


def disconnect_request() -> bytes:
    """Sends a disconnection request to server with status code of 000"""
    payload = VERSION_LEN + ENC_VERSION_2 + ENC_DISCONN_LEN + ENC_DISCONN_REQ + DISCONN_CODE.encode(FORMAT)
    header = struct.pack("!I", len(payload))

    request = header + payload 
    return request
