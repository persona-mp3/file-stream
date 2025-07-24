import struct 
from utils.utils import file_handler

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
    header = struct.pack("!I", payload)

    packet = header + payload

    print()
    print(packet)
    print()

    return packet


def mock_data(file_name: str):
    file = file_handler(file_name, "rb")
    while True:
        content = file.read(CHUNK_SIZE)
        if not content:
            print("EOF")
            file.close()
            break
        encode_packet_v1(content)
