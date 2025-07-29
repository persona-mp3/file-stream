import struct

HEADER = 4  # The size of the header in bytes
FORMAT = "utf-8"
STATUS_S = "200"
STATUS_F = "400"
PACKET_REQ = "Packet"
PACKET_ACK = "Packet-Status"


def decode_packet(packet: bytes) -> int:
    """
    This is the main decoding logic for Data-Packets. Here is the packet structure:

    ===================================================
            Content-Length: 4 bytes, BigEndian
            Request-Type-Len: 1 byte
            Request-Type : encoded-byte-data
            Packets-Sent-Len: 4bytes, BigEndian
            Packets-Sent: encoded-byte-data
            Tag-Len: 4bytes, BigEndian
            Tag: 4bytes, BigEndian
            Data: encoded-byte-data
    ===================================================

    Theres always an offset increase based on where the current slicing position you are at.
    You should be careful editing this unless you want to go bald early

    This function decodes the packet receives from a client. This function will appear to have this signature:
    decode_packet(client: socket, cwd: str, author: str) -> int
    The cwd and author are gotten from the ACK request-response, which is sent by the client before sending the data-packet.

    But for testing sake, it has this signature:
    decode_packet(client: socket, cwd: str, author: str) -> tuple
    """

    header = packet[:4]
    content_len = struct.unpack("!I", header)[0]

    print("\n === full packet loaded, decoding === \n")
    payload = packet[4: 4 + content_len]
    print(payload)

    offset = 0
    req_type_len = struct.unpack("B", payload[:1])[0]

    # we are currently on the second byte, since we read 1st byte ->  [0, 1, 2 ... nth]
    offset += 1
    req_type = payload[offset: offset + req_type_len].decode(FORMAT)
    # we might also check the type of request sent and validate against it
    print(f"Request-Type: {req_type}")
    offset += req_type_len

    sent_packets_len = struct.unpack("!I", payload[offset: offset + 4])[0]
    offset += 4

    sent_packets = payload[offset: offset + sent_packets_len].decode(FORMAT)
    print(f"Client-Sent: {sent_packets}")
    offset += sent_packets_len

    tag_len = struct.unpack("!I", payload[offset: offset + 4])[0]
    offset += 4

    tag = payload[offset: offset + tag_len].decode(FORMAT)
    print(f"Current tag for packet: {tag}")
    offset += tag_len

    data = payload[offset:].decode(FORMAT)

    print("transferring data ")

    return (content_len, req_type, sent_packets, tag, data)


def mock_data() -> bytes:

    req_type = PACKET_REQ.encode(FORMAT)
    enc_req_len = struct.pack("!B", len(req_type))

    sent_packets = "5".encode(FORMAT)
    enc_sent_packets_len = struct.pack("!I", len(sent_packets))

    tag = "5".encode(FORMAT)
    enc_tag_len = struct.pack("!I", len(tag))

    data = "Test Data".encode(FORMAT)

    payload = enc_req_len + req_type + enc_sent_packets_len + sent_packets + enc_tag_len + tag + data
    header = struct.pack("!I", len(payload))

    packet = header + payload
    return packet


# decode_packet(mock_data())
