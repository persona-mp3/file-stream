import struct
from encoders.pack_response import send_packet_status, verify_packet_status

FORMAT = "utf-8"
STATUS_S = "200"
STATUS_F = "400"
PACKET_REQ = "Packet"
PACKET_ACK = "Packet-Status"


def test_send_packet_status():
    """
    We are testing the send_packet_status function to ensure it correctly formats the packet status response.
    """
    tag = 12
    recvd = 20
    req_type = "Packet-Status"

    enc_req_type = (req_type + " \r\n").encode(FORMAT)
    enc_tag = (str(tag) + " \r\n").encode(FORMAT)
    enc_recvd = (str(recvd) + " \r\n").encode(FORMAT)
    expects = (str(tag + 1) + " \r\n").encode(FORMAT)
    enc_stats = (STATUS_S + " \r\n").encode(FORMAT)

    payload = enc_req_type + enc_tag + enc_stats + enc_recvd + expects
    header = struct.pack("!I", len(payload))

    packet = header + payload

    assert send_packet_status(tag, recvd) == packet


def test_verify_packet_status_false():
    """
    The verify_packet_status function should return False, if the packet it received is an invalid packet, ie 
    - The packet is not a PACKET_ACK type, ie Packet-Status
    - The status code is not 200, ie STATUS_S
    """
    tag = 12
    recvd = 20
    req_type = "Packet-Status"

    enc_req_type = (req_type + " \r\n").encode(FORMAT)
    enc_tag = (str(tag) + " \r\n").encode(FORMAT)
    enc_recvd = (str(recvd) + " \r\n").encode(FORMAT)
    expects = (str(tag + 1) + " \r\n").encode(FORMAT)
    enc_stats = (STATUS_F + " \r\n").encode(FORMAT)

    payload = enc_req_type + enc_tag + enc_stats + enc_recvd + expects
    header = struct.pack("!I", len(payload))

    packet = header + payload
    ok = False

    assert verify_packet_status(packet) == ok


def test_verify_packet_status_true():
    """
    The verify_packet_status function should return True, if the packet it receives has status of 200
    """
    tag = 12
    recvd = 20
    req_type = "Packet-Status"

    enc_req_type = (req_type + " \r\n").encode(FORMAT)
    enc_tag = (str(tag) + " \r\n").encode(FORMAT)
    enc_recvd = (str(recvd) + " \r\n").encode(FORMAT)
    expects = (str(tag + 1) + " \r\n").encode(FORMAT)
    enc_stats = (STATUS_S + " \r\n").encode(FORMAT)

    payload = enc_req_type + enc_tag + enc_stats + enc_recvd + expects
    header = struct.pack("!I", len(payload))

    packet = header + payload
    ok = True

    assert verify_packet_status(packet) == ok


test_send_packet_status()
test_verify_packet_status_true()
test_verify_packet_status_false()
