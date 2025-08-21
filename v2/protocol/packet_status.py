import struct 
from .encoder import encoder 

from v2.constants.constants import (FORMAT, OPP_RES, CLOSE_CONNECTION)


def controller(packet: bytes) -> tuple[str, bytes]:
    """
    Packet must not contain header from server.
    Returns status-code of the response, and its remaining payload.
    If the status-code is in ```CLOSE_CONNECTION```, the bytes returned will be empty
    """
    STATUS_CODE = ""
    PAYLOAD = b''

    # read version
    offset = 0
    version_len = packet[:1]
    offset += 1
    version_len = struct.unpack("B", version_len)[0]
    version = packet[offset: version_len]
    offset += version_len

    # read request-type 
    request_len = packet[offset: offset + 1]
    offset += 1
    request_len = struct.unpack("B", request_len)[0]
    request_type = packet[offset: offset + request_len]
    offset += request_len

    # read status code so the client-script can use it take actions depending
    status_code_len = packet[offset: offset + 1]
    offset += 1
    status_code_len = struct.unpack("B", status_code_len)[0]
    status_code = packet[offset: offset + status_code_len].decode(FORMAT)
    offset += status_code_len

    remaining_payload = packet[offset:]

    if request_type.decode(FORMAT) in CLOSE_CONNECTION:
        STATUS_CODE = status_code
    else:
        STATUS_CODE = status_code
        PAYLOAD = remaining_payload

    return STATUS_CODE, PAYLOAD


def main() -> None:
    packet = encoder(1, 1, "Montagem Core Titanium".encode(FORMAT))
    print(controller(packet[4:]))


if __name__ == "__main__":
    main()
