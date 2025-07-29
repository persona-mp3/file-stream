import struct 
from typing import NamedTuple

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


class PacketInfoTest(NamedTuple):
    """ Packet-Info holds the content_length: int, req_type, packets_sent, tag and data are all str """
    content_length: int
    version: str
    req_type: str
    packets_sent: str
    tag: str
    data: str


class PacketInfo(NamedTuple):
    """
    Holds Version, Request-Type, Sent, Tag, and data all in string
    """
    version: str
    req_type: str
    sent: str
    tag: str
    data: str


def decode_packet_logic(packet: bytes) -> PacketInfoTest:
    """
    This  function is mainly for testing purposes, the main function that will be used to decode the content from the socket will be down below.

    The data-slicing here involves incrementing the offset position for every peice of data we read, after we get the length of a speicified feild 
    we increment the offset to keep track of out current position in the buffer/packet.

    Decoding Logic for Packets sent by client

    Returns:
        - None: If the version is not supported. At this stage, aything other than "001"

    """
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

    if version.decode(FORMAT) != VERSION:
        print(f"Invalid version {version}, return TeaCup")
        return

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
    print(f"Data in packet:\n {data.decode(FORMAT)}")

    return PacketInfoTest(decoded_content_len, version.decode(FORMAT), req_type.decode(FORMAT), 
                          packets_sent.decode(FORMAT), tag.decode(FORMAT), data.decode(FORMAT))


def decode_packet(packet: bytes) -> PacketInfo:
    """
    Decodes packet request from raw socket data

    Precondition:
        -The content-length of the packet must be known first and the whole packet extracted, before using decode_packet

    Caller:
        - Typically used in recv_data(client: socket)

    Returns:
        - PacketInfo(version, req_type, sent, tag, data)
        - None if the packet is malformed or has an invalid version
    """
    offset = 0
    version_len = packet[:1]
    offset += 1 

    version_len = struct.unpack("B", version_len)[0]
    version = packet[offset: offset + version_len]
    print(f"Request Version: {version}")
    if version != VERSION:
        print(f"Invalid Version/Malformed Packet: {version.decode(FORMAT)}")
        return

    offset += version_len

    req_len = packet[offset: offset + 1]
    offset += 1
    req_len = struct.unpack("B", req_len)[0]
    req_type = packet[offset: offset + req_len]
    print(f"Request-Type: {req_type}")
    offset += req_len

    # Because the n_packets was encoded in BigEndian, we read the next for bytes
    sent_len = packet[offset: offset + 4]
    offset += 4
    sent_len = struct.unpack("!I", sent_len)[0]

    sent_packets = packet[offset:offset + sent_len]
    print(f"Number of packets sent: {sent_packets}")
    offset += sent_len

    tag_len = packet[offset: offset + 4]
    offset += 4
    tag_len = struct.unpack("!I", tag_len)[0]
    tag = packet[offset: offset + tag_len]
    print(f"Tag of current packet: {tag}")
    offset += tag_len

    data = packet[offset:]
    print(f"Data inside packet:\n ==== \n {data} \n === \n")

    return PacketInfo(version.decode(FORMAT), req_type.decode(FORMAT), 
                      sent_packets.decode(FORMAT), tag.decode(FORMAT), 
                      data.decode(FORMAT))
