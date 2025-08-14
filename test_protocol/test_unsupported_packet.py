import struct 
import hashlib
import pytest

from v2.protocol import decoder as dec 
from v2.constants.constants import (FORMAT, ENC_PACKET_REQ, ENC_PACKET_REQ_LEN)


def encode_unsupported_version(packet_tag: int, sent_packets: int, data: bytes) -> bytes:
    """
    Unit test for the decoding malformed packet. For this test, an unsupported parameter will be used
    against it. 

    The decoder should raise an UnsupportedError when it detects this

    Structure:
        (4B content-length/header) (1B version-len)(version)
        (1B request-length)(request-type)
        (4B packet-sent-length)(packet-sent)
        (4B packet-tag-length)(packet-tag)
        (1B checksum-length)(checksum)
        (data)

    Returns:
        Fully encoded packet with tampered data
    """

    UNSUPPORTED_VERSION = "New Version"

    enc_sent = str(sent_packets).encode(FORMAT)
    sent_len = struct.pack("!I", len(enc_sent))

    enc_tag = str(packet_tag).encode(FORMAT)
    tag_len = struct.pack("!I", len(enc_tag))

    checksum = hashlib.sha256(data).hexdigest().encode(FORMAT)
    checksum_len = struct.pack("B", len(checksum))

    payload = (
        struct.pack("B", len(UNSUPPORTED_VERSION)) + UNSUPPORTED_VERSION.encode(FORMAT) +
        ENC_PACKET_REQ_LEN + ENC_PACKET_REQ + 
        sent_len + enc_sent + tag_len + enc_tag +
        checksum_len + checksum + data
    )

    header = struct.pack("!I", len(payload))
    packet = header + payload
    print("\n\n", packet)
    return packet


def test_corrupted_packet() -> None:
    data = "This packet will be tampered with".encode(FORMAT)
    tag = 0
    sent = 0
    expected_data = encode_unsupported_version(tag, sent, data)

    with pytest.raises(dec.UnsupportedError) as exception_info:
        dec.decoder(expected_data[4:])

    print(exception_info)
