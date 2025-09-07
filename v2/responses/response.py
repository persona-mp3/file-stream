import struct 
import uuid

from ..logger.logger import create_logger
from ..constants.constants import (
    VERSION_LEN, ENC_VERSION_2, ENC_ACK_REQ, 
    ACK_VERSION_2, FORMAT, ACK_S,

    ENC_PACKET_RES, ENC_PACKET_RES_LEN, ENC_ACK_F,

    ENC_OPP_RES_LEN, ENC_OPP_RES, OPP_CODE,
    ENC_UNSUPPORTED_RES, ENC_UNSUPPORTED_LEN, UNSUPPORTED_CODE, 

    ENC_CORRUPTED_RES_LEN, ENC_CORRUPTED_RES, CORRUPTED_CODE,

    ENC_MALF_RES_LEN, ENC_MALF_RES, MALF_CODE,
    ENC_RETRY_RES, ENC_RETRY_RES_LEN, RETRY_CODE,
)

"""
## All Responses are in byte protocol, except Ack-Request, 

Response Structure:
    (4B content-length) (1B version-len)(version)
    (1B request-length)(request-type)
    (1B status-code-length)(status-code)

Response functions that take in data like tag, recd packets have 
a different structure as they relay information back to the client. 
Responses like Retry, Packet-Status and more. The new data will be appended to the response body 
instead.

For example, packet-status response would have the following structure as it sends information about
the current packet, it's own received packet and expected-packet 
        (4B content-length)(1B version-length)(version)
        (1B request-length)(request-type)(1B status-code-length)(status-code)
        (1B tag-len)(tag)(1B recvd-len)(recvd-packets)
        (1B expected-packet-len)(expected-packet)
"""

logger = create_logger()


def ack_response(is_valid: bool) -> tuple[bytes, str]:
    """
    Creates an Ack-Response to send to client.
    If ```is_valid``` is set to False, and ack-status of 400 will be made which means 
    that the server failed to Acknowledge the client and 200, otherwise with a ```session_id``` 
    appended at the end of response. This response is delimited by a carriage return.

    The Caller is responsible for validating the request first.

    Structure:
        (version)(response-type)(status)(session-id?)

    Returns:
        fully encoded response, sessionId

    """

    session_id = f"{uuid.uuid4()} \r\n".encode(FORMAT)

    base_body = ACK_VERSION_2 + ENC_ACK_REQ 
    body = None
    if is_valid:
        body = f"{ACK_S} \r\n".encode(FORMAT) + session_id
    else:
        body = ENC_ACK_F 

    payload = base_body + body

    header = struct.pack("!I", len(payload))
    response = header + payload
    return (response, session_id.decode(FORMAT).rstrip(" \r\n"))


def packet_stats2(tag: int, recvd: int, retry: bool) -> bytes:
    """
    ```tag``` and ```recvd``` are provided by the caller to encode into the response the packet that was 
    successful and the number of packets received. 

    If the ```retry``` argument is provided as ```True```, a packet-status code of ```201``` would be 
    sent to the client for retrial of that particular packet. The ```expected-packet``` field will 
    match the ```packet-tag``` instead of a +1 of the tag

    Structure:
        (4B content-length)(1B version-length)(version)
        (1B request-length)(request-type)(1B status-code-len)(status-code)
        (1B tag-len)(tag)(1B recvd-len)(recvd-packets)
        (1B expected-packet-len)(expected-packet)

    Returns:
        Encoded Response
    """

    enc_tag = f"{tag}".encode(FORMAT)
    tag_len = struct.pack("B", len(enc_tag))
    enc_recvd = f"{recvd}".encode(FORMAT)
    recvd_len = struct.pack("B", len(enc_recvd))
    enc_expected = f"{tag + 1}".encode(FORMAT)
    expected_len = struct.pack("B", len(enc_expected))

    BASE_BODY = VERSION_LEN + ENC_VERSION_2 

    body = None
    if retry:
        body = (
            ENC_RETRY_RES_LEN + ENC_RETRY_RES + 
            struct.pack("B", len(RETRY_CODE.encode(FORMAT))) + RETRY_CODE.encode(FORMAT) + 
            tag_len + enc_tag + recvd_len + enc_recvd + tag_len + enc_tag
        )
    else:
        body = (
            ENC_PACKET_RES_LEN + ENC_PACKET_RES + 
            struct.pack("B", len(ACK_S.encode(FORMAT))) + ACK_S.encode(FORMAT) + 
            tag_len + enc_tag + recvd_len + enc_recvd + expected_len + enc_expected
        )

    payload = BASE_BODY + body
    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def operational_response(packet_tag: str = None, author: str = None, checksum: str = None, offset: int = None) -> bytes:
    """
    Returns a packet of ```Operational``` Response and status code of `500`.
    This is to be used when using external APIs throw errors or unexpected exceptions.

    If it occurs while reading from a client, it is essential that you pass in the packet-tag, 
    and author for retrials
    """

    if all(parameter is not None for parameter in (packet_tag, author, checksum, offset)):
        print("Error occurred while reading from client, logging values")
        logger.info(
            f"Operational Err: packet-tag: {(packet_tag)}, author: {(author)},  checksum: {(checksum)}\noffset: {(offset)}"
        )

    payload = (
        VERSION_LEN + ENC_VERSION_2 + ENC_OPP_RES_LEN + ENC_OPP_RES +
        struct.pack("B", len(OPP_CODE.encode(FORMAT))) + OPP_CODE.encode(FORMAT)
    )

    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def unsupported_response() -> bytes:
    """Encodes a response of type ```Unsupported``` with status code of 444"""
    payload = (
        VERSION_LEN + ENC_VERSION_2 + ENC_UNSUPPORTED_LEN + ENC_UNSUPPORTED_RES + 
        struct.pack("B", len(UNSUPPORTED_CODE.encode(FORMAT))) + UNSUPPORTED_CODE.encode(FORMAT)
    )

    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def corrupted_response() -> bytes:
    """Encodes a response of type ```Corrupted``` with status code of 399"""
    payload = (
        VERSION_LEN + ENC_VERSION_2 + ENC_CORRUPTED_RES_LEN + 
        ENC_CORRUPTED_RES + 
        struct.pack("B", len(CORRUPTED_CODE.encode(FORMAT))) + CORRUPTED_CODE.encode(FORMAT)
    )

    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def malformed_response() -> bytes:
    """Encodes a response of type ```Malformed``` with status code of 401"""
    payload = (
        VERSION_LEN + ENC_VERSION_2 + ENC_MALF_RES_LEN + 
        ENC_MALF_RES + struct.pack("B", len(MALF_CODE.encode(FORMAT))) +
        MALF_CODE.encode(FORMAT)
    )

    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def accept_reconnect(is_valid: bool) -> tuple[bytes, str]:
    """
    Creates an Ack-Response to send to client.
    If ```is_valid``` is set to False, and ack-status of 400 will be made which means 
    that the server failed to Acknowledge the client and 200, otherwise with a ```session_id``` 
    appended at the end of response. This response is delimited by a carriage return.

    The Caller is responsible for validating the request first.

    Structure:
        (version)(response-type)(status)(session-id?)

    Returns:
        fully encoded response, sessionId

    """

    session_id = f"{uuid.uuid4()} \r\n".encode(format)
    base_body = ACK_VERSION_2 + ENC_ACK_REQ 
    body = None
    if is_valid:
        body = f"{ACK_S} \r\n".encode(FORMAT) + session_id
    else:
        body = ENC_ACK_F 

    payload = base_body + body

    header = struct.pack("!I", len(payload))
    response = header + payload
    return (response, session_id.decode(FORMAT).rstrip(" \r\n"))
