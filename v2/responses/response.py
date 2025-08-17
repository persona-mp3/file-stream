import struct 
import uuid

from ..logger.logger import create_logger
from ..constants.constants import (
    VERSION_LEN, ENC_VERSION_2, ENC_ACK_REQ, 

    ACK_VERSION_2, FORMAT, ACK_S,

    ENC_ACK_RES, ENC_ACK_S, ENC_ACK_F,

    ENC_OPP_RES_LEN, ENC_OPP_RES, OPP_CODE,

    ENC_UNSUPPORTED_RES, ENC_UNSUPPORTED_LEN, UNSUPPORTED_CODE, 

    ENC_CORRUPTED_RES_LEN, ENC_CORRUPTED_RES, CORRUPTED_CODE,

    ENC_MALF_RES_LEN, ENC_MALF_RES, MALF_CODE,
)

"""
## All Responses are in byte protocol, except Ack-Request

Response Structure:
    (4B content-length) (1B version-len)(version)
    (1B request-length)(request-type)(status-code)
"""

logger = create_logger()


def ack_response(is_valid: bool) -> tuple[bytes, str]:
    """
    Creates an Ack-Response to send to client.
    If ```is_valid``` is set to False, and ack-status of 400 will be made which means 
    that the server failed to Acknowlegde the client and 200, otherwise with a ```session_id``` 
    appended at the end of response. This repsonse is delimited by a carraige return.

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


def operational_response(packet_tag: str = None, author: str = None, checksum: str = None, offset: int = None) -> bytes:
    """
    Returns a packet of ```Operational``` Response and status code of `500`.
    This is to be used when using external API's throw errors or unexpected excpetions.

    If it occurs while reading from a client, it is essential that you pass in the packet-tag, 
    and author for retrials
    """

    if all(parameter is not None for parameter in (packet_tag, author, checksum, offset)):
        print("Error occured while reading from client, logging values")
        logger.info(
            f"Operational Err: packet-tag: {(packet_tag)}, author: {(author)},  checksum: {(checksum)}\noffset: {(offset)}"
        )

    payload = (
        VERSION_LEN + ENC_VERSION_2 +
        ENC_OPP_RES_LEN + ENC_OPP_RES + OPP_CODE.encode(FORMAT)
    )

    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def unsupported_response() -> bytes:
    """Encodes a response of type ```Unsupported``` with status code of 444"""
    payload = (
        VERSION_LEN + ENC_VERSION_2 + ENC_UNSUPPORTED_LEN + 
        ENC_UNSUPPORTED_RES + UNSUPPORTED_CODE.encode(FORMAT)
    )

    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def corrupted_response() -> bytes:
    """Encodes a response of type ```Corrupted``` with status code of 399"""
    payload = (
        VERSION_LEN + ENC_VERSION_2 + ENC_CORRUPTED_RES_LEN + 
        ENC_CORRUPTED_RES + CORRUPTED_CODE.encode(FORMAT)
    )

    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def malformed_response() -> bytes:
    """Encodes a response of type ```Malformed``` with status code of 401"""
    payload = (
        VERSION_LEN + ENC_VERSION_2 + ENC_MALF_RES_LEN + 
        ENC_MALF_RES + MALF_CODE.encode(FORMAT)
    )

    header = struct.pack("!I", len(payload))
    response = header + payload
    return response
