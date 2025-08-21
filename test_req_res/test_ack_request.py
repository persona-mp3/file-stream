import struct 
from pathlib import Path

from v2.constants.constants import (FORMAT, ACK_VERSION_2, ENC_ACK_REQ)
from v2.requests import request as req


def create_ack_request(author: bytes, cwd: bytes, n_packets: bytes) -> bytes:

    payload = (ACK_VERSION_2 + ENC_ACK_REQ + n_packets + cwd + author)
    header = struct.pack("!I", len(payload))

    request = header + payload
    return request


def test_ack_request():
    cwd = f"{Path.cwd().name} \r\n".encode(FORMAT)
    author = "main.go \r\n".encode(FORMAT)
    n_packets = "12 \r\n".encode(FORMAT)
    expected_request = create_ack_request(author, cwd, n_packets)

    assert req.ack_request("main.go", f"{Path.cwd().name}", 12) == expected_request
