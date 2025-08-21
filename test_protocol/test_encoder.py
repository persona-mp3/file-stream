import struct 
import hashlib

from v2.protocol import encoder as enc 
# from v2.constants.constants import (FORMAT, ENC_VERSION_2, VERSION_LEN, PACKET_REQ, PACKET_REQ_LEN)
from v2.constants.constants import (
    FORMAT, ENC_VERSION_2, VERSION_LEN, 
    ENC_PACKET_REQ, ENC_PACKET_REQ_LEN
)


def manual_encode(packet_tag: int, sent_packets: int, data: bytes) -> bytes:
    """
    Unit test for encoder. The encoder should return the following structure:

    Structure:
        (4B content-length/header) (1B version-len)(version)
        (1B request-length)(request-type)
        (4B packet-sent-length)(packet-sent)
        (4B packet-tag-lenght)(packet-tag)
        (1B checksum-length)(checksum)
        (data)

    Returns:
        Fully encoded packet
    """
    enc_sent = str(sent_packets).encode(FORMAT)
    sent_len = struct.pack("!I", len(enc_sent))

    enc_tag = str(packet_tag).encode(FORMAT)
    tag_len = struct.pack("!I", len(enc_tag))

    checksum = hashlib.sha256(data).hexdigest().encode(FORMAT)
    checksum_len = struct.pack("B", len(checksum))

    payload = (
        VERSION_LEN + ENC_VERSION_2 +
        ENC_PACKET_REQ_LEN + ENC_PACKET_REQ + 
        sent_len + enc_sent + tag_len + enc_tag +
        checksum_len + checksum + data
    )

    header = struct.pack("!I", len(payload))
    packet = header + payload
    return packet


def test_encoder() -> None:
    data = "Joe Rogan Experience: #2252".encode(FORMAT)
    tag = 0
    sent = 0
    expected_data = manual_encode(tag, sent, data)

    assert enc.encoder(tag, sent, data) == expected_data
