import struct
from encoders.decode_packet import decode_packet

FORMAT = "utf-8"
STATUS_S = "200"
STATUS_F = "400"
PACKET_REQ = "Packet"
PACKET_ACK = "Packet-Status"


def test_decode_packet():
    """
    Here, we are manullay encoding a packet that the decode_packet function should be able to decode. 
    The test validates whether the content returned by decode_packet is as expected.
    """
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

    # decoded representation that decode packet should sent
    content_len = len(payload)

    assert decode_packet(packet) == (content_len, PACKET_REQ, sent_packets.decode(FORMAT), tag.decode(FORMAT), data.decode(FORMAT))  


test_decode_packet()
