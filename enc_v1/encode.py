import struct 

VERSION = "001"
# encoding and decoding format byte-based protocols
FORMAT = "utf-8"
ENC_VERSION = VERSION.encode(FORMAT)
PACKED_VERSION_LEN = struct.pack("B", len(ENC_VERSION))


# Request-Type to let the serve know this is indeed a data packet
PACKET_REQ = "Packet"
ENC_PACKET_REQ = PACKET_REQ.encode(FORMAT)
PACKED_PACKET_LEN = struct.pack("B", len(ENC_PACKET_REQ))

# Response from the server on the packet we just sent
PACKET_RES = "Packet-Status"


def encode_packet(data: bytes, tag: int, sent: int) -> bytes:
    enc_tag = str(tag).encode(FORMAT)
    enc_sent = str(sent).encode(FORMAT)
    enc_tag_len = struct.pack("!I", len(enc_tag))
    enc_sent_len = struct.pack("!I", len(enc_sent))

    payload = PACKED_VERSION_LEN + ENC_VERSION + PACKED_PACKET_LEN + ENC_PACKET_REQ + enc_sent_len + enc_sent + enc_tag_len + enc_tag + data
    header = struct.pack("!I", len(payload))

    packet = header + payload

    print(f"Stats: Content-Length: {len(payload)}")
    # print(packet)
    print()

    return packet
