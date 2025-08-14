import struct 
import hashlib
import pytest

from v2.protocol.decoder import decoder, CorruptionError
from v2.constants.constants import (FORMAT, ENC_VERSION_2, VERSION_LEN, ENC_PACKET_REQ, ENC_PACKET_REQ_LEN)


def encode_corrupted_packet(packet_tag: int, sent_packets: int, data: bytes) -> bytes:
    """
    Unit test for the decoding corrupted data. The data passed has a sha256 checksum computed 
    against it. If any changes are made to this data, the checksum will be different. 

    The decoder should raise a CorruptedError when it detects this

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
    # modify the data
    # corrupted_data = data.decode(FORMAT)
    corrupted_data = f"{data.decode(FORMAT)} data has been corrupted by tampering thereby invalidating the checkum"
    corrupted_data = corrupted_data.encode(FORMAT)

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
        checksum_len + checksum + corrupted_data
    )

    header = struct.pack("!I", len(payload))
    packet = header + payload
    print("\n\n", packet)
    return packet


def test_corrupted_packet() -> None:
    data = "This packet will be tampered with".encode(FORMAT)
    tag = 0
    sent = 0
    expected_data = encode_corrupted_packet(tag, sent, data)

    with pytest.raises(CorruptionError) as exception_info:
        decoder(expected_data[4:])

    assert "Client checksum and built checksum are not the same" in str(exception_info.value)
