import struct 
from enc_v1 import encode as v1

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


def manually_encode(data: bytes, tag: int, sent: int) -> bytes:
    enc_tag = str(tag).encode(FORMAT)
    enc_sent = str(sent).encode(FORMAT)
    enc_tag_len = struct.pack("!I", len(enc_tag))
    enc_sent_len = struct.pack("!I", len(enc_sent))

    base_payload = PACKED_VERSION_LEN + ENC_VERSION + PACKED_PACKET_LEN + ENC_PACKET_REQ 
    body = base_payload + enc_sent_len + enc_sent + enc_tag_len + enc_tag + data
    header = struct.pack("!I", len(body))

    packet = header + body
    return packet


def test_v1_encoding() -> None:
    data = "Test Data: Standing Tall".encode(FORMAT)
    tag = 1
    sent = 1

    assert v1.encode_packet(data, tag, sent) == manually_encode(data, tag, sent)
