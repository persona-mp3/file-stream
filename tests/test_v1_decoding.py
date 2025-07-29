import struct 
# imports all the files from enc_v1
from enc_v1 import * 


VERSION = "001"
FORMAT = "utf-8"
ENC_VERSION = VERSION.encode(FORMAT)
PACKED_VERSION_LEN = struct.pack("B", len(ENC_VERSION))


# Request-Type to let the serve know this is indeed a data packet
PACKET_REQ = "Packet"
ENC_PACKET_REQ = PACKET_REQ.encode(FORMAT)
PACKED_PACKET_LEN = struct.pack("B", len(ENC_PACKET_REQ))

# Response from the server on the packet we just sent
PACKET_RES = "Packet-Status"


def test_v1_decoding() -> None:
    test_data = "Honest Question: Oakwood Station".encode(FORMAT)
    tag = 11
    sent = 11

    packet = encode.encode_packet(test_data, tag, sent)
    content_length = struct.unpack("!I", packet[:4])[0]
    expected_data = (content_length, VERSION, PACKET_REQ, str(sent), str(tag), test_data.decode(FORMAT))

    assert decode.decode_packet_logic(packet) == expected_data


def manually_encode(data: bytes, tag: int, sent: int) -> bytes:
    """Manually Encode with invalid version"""
    enc_tag = str(tag).encode(FORMAT)
    enc_sent = str(sent).encode(FORMAT)
    enc_tag_len = struct.pack("!I", len(enc_tag))
    enc_sent_len = struct.pack("!I", len(enc_sent))

    INVALID_VERSION = "002".encode(FORMAT)
    PACKED_INVALID_VERSION = struct.pack("!I", len(INVALID_VERSION))
    base_payload = PACKED_INVALID_VERSION + INVALID_VERSION + PACKED_PACKET_LEN + ENC_PACKET_REQ 
    body = base_payload + enc_sent_len + enc_sent + enc_tag_len + enc_tag + data

    header = struct.pack("!I", len(body))

    packet = header + body
    return packet


def test_v1_decoding_invalid_version() -> None:
    """Expect the decoder to return None if the Version is invalid"""
    test_data = "Ain't that So?: Oakwood Station".encode(FORMAT)
    tag = 11
    sent = 11

    invalid_packet = manually_encode(test_data, tag, sent)
    # Will configure to send an Invalid response, something stating that the 
    # "I don't know what Version you're talking about I only understand 001"
    expected_data = None

    assert decode.decode_packet_logic(invalid_packet) == expected_data

    ...
