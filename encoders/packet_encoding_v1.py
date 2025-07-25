import struct 
# from utils.utils import file_handler

VERSION = "001"
# encoding and decoding format byte-based protocols
FORMAT = "utf-8"
ENC_VERSION = VERSION.encode(FORMAT)
PACKED_VERSION_LEN = struct.pack("B", len(ENC_VERSION))

# The amount of bytes to first read from the socket-client to get the content-length. (encoded in 4bytes, BigEndian)
HEADER = 4
# The amount of bytes we want to read from the file before EOF
CHUNK_SIZE = 1024

# Request-Type to let the serve know this is indeed a data packet
PACKET_REQ = "Packet"
ENC_PACKET_REQ = PACKET_REQ.encode(FORMAT)
PACKED_PACKET_LEN = struct.pack("B", len(ENC_PACKET_REQ))

# Response from the server on the packet we just sent
PACKET_RES = "Packet-Status"


def encode_packet_v1(data: bytes, author: str = "packet_encoding.py", tag: int = 12, sent: int = 12) -> bytes:
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


def decode_packet_v1(packet: bytes) -> tuple:
    offset = 0
    content_len = packet[:4]
    offset += 4

    decoded_content_len = struct.unpack("!I", content_len)[0]
    print(f"Content-Length of packet -> {decoded_content_len}")

    version_len = packet[offset: offset + 1]
    offset += 1

    version_len = struct.unpack("B", version_len)[0]
    version = packet[offset: offset + version_len]
    print(f"Version: {version}")

    offset += version_len

    req_type_len = packet[offset: offset + 1]
    offset += 1

    req_len = struct.unpack("B", req_type_len)[0]
    req_type = packet[offset: offset + req_len]
    print(f"The Request-Type: {req_type}")

    offset += req_len

    sent_len = packet[offset: offset + 4]
    sent_len = struct.unpack("!I", sent_len)[0]
    offset += 4
    packets_sent = packet[offset: offset + sent_len]
    print(f"Packets-Sent {packets_sent}")

    offset += sent_len
    tag_len = packet[offset: offset + 4]
    offset += 4

    tag_len = struct.unpack("!I", tag_len)[0]
    tag = packet[offset: offset + tag_len]
    offset += tag_len
    print(f"Tag: {tag}")

    data = packet[offset:]
    print(f"Data in packet:\n {data.encode(FORMAT)}")

    return (content_len, req_type, packets_sent, tag, data)
