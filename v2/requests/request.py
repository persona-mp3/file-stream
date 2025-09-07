import struct 

from ..logger.logger import create_logger
from ..constants.constants import (
    ACK_VERSION_2, VERSION_LEN, ENC_VERSION_2, 
    FORMAT, ENC_ACK_REQ,
    ENC_DISCONN_LEN, ENC_DISCONN_REQ, DISCONN_CODE
)


logger = create_logger()


def ack_request(author: str, CWD: str, n_packets: int) -> bytes:
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


def ack_reconnect(session_id: str, author: str, CWD: str, file_cksum: str, data_cksum: str, last_packet_id: str, n_packets: str, ) -> bytes:
    # we can make this string based, but since we will only require their session_id and 
    # the function should also take the last packet-sent, and it's checksum included 
    # and filename. So the data can be modelled as thus in redis:
    # session_id: { author: "retry.py", "id": 21, data-cksum: "abcd", "n_packets", 20, file_cksum: "efght"}
    # the data-cksum is gotten from the packet, while the file-ckusm is gotten from hashing the file the client claims
    # for additional security TLS verification will be needed or ssh verification, but the session-id is based on uuid assinged 
    # during ack-response
    # the data used will be that used in test cases. See ../../concepts/retrial.txt
    enc_cwd = f"{CWD} \r\n".encode(FORMAT)
    enc_author = f"{author} \r\n".encode(FORMAT)

    session_id = f"{session_id} \r\n".encode(FORMAT)
    file_cksum = f"{file_cksum} \r\n".encode(FORMAT)
    packet_id = f"{last_packet_id} \r\n".encode(FORMAT)
    n_packets = f"{n_packets} \r\n".encode(FORMAT)
    data_cksum = f"{data_cksum} \r\n".encode(FORMAT)

    payload = (
        ACK_VERSION_2 + ENC_ACK_REQ + session_id + enc_author + enc_cwd + file_cksum + 
        packet_id + data_cksum + n_packets 
    )
    header = struct.pack("!I", len(payload))

    request = header + payload
    return request


def disconnect_request() -> bytes:
    """Sends a disconnection request to server with status code of 000"""
    payload = (
        VERSION_LEN + ENC_VERSION_2 + ENC_DISCONN_LEN + ENC_DISCONN_REQ +
        struct.pack("B", len(DISCONN_CODE.encode(FORMAT))) + DISCONN_CODE.encode(FORMAT)
    )
    header = struct.pack("!I", len(payload))

    request = header + payload 
    return request
