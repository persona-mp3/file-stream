import struct

FORMAT = "utf-8"
PACKET_ACK = "Packet-Status \r\n".encode(FORMAT)
STATUS_S = "200 \r\n".encode(FORMAT)
STATUS_F = "400 \r\n".encode(FORMAT)

# this could also take a socket argument. If no exception was raised during the whole packet operation, 
# we could just send default as success


def send_packet_status(tag: int = 12, n_packets: int = 20) -> bytes: 
    """
    This is used on the server side, to tell the client, that the nth-packet they sent, was received successfully
    This request is text-based, so there is no need for extreme byte manipulation.
    It contains the current-packet tag it just recieved, the status and what the next tag it is expecting. 

    So the format is something like this:

    Request-Type: Packet-Status \r\n
    Tag: 12 \r\n
    Status: 200 \r\n 200 means success, 400 failed (packet misalignment). 
    Received: 8 \r\n
    Expecting: 13 \r\n

    The Expecting field is gotten from subtracting the N_PACKETS the client had sent in the ACK-Request-Response, 
    and the Current-tag in the current-packet which can be found while decoding the data-packet
    """
    expecting = (str(tag + 1) + " \r\n").encode(FORMAT)
    # in this case, we would want to use a loop to keep track instead
    received = (str(n_packets - tag) + " \r\n").encode(FORMAT)
    body = PACKET_ACK + (str(tag) + " \r\n").encode(FORMAT) + STATUS_F + received + expecting 
    header = struct.pack("!I", len(body))

    packet = header + body
    return packet


def verify_packet_status(packet: bytes) -> bool:
    # read the first 4bytes to get the content-length
    """
    This is used to decode the Acknowledge response for the Packet-Status type of Request

    Content-Len: 4bytes
    Request-Type: PACKET_ACK \r\n
    Tag: str \r\n
    Status: str \r\n
    Received: str \r\n
    Expecting: str \r\n
    """
    ok = True
    content_len = packet[:4]
    content_len = struct.unpack("!I", content_len)[0]
    print("\n === verifying last packet sent === \n")

    payload = packet[4: content_len + 4].decode(FORMAT).split()
    if payload[0] != PACKET_ACK.decode(FORMAT).rstrip():
        print("This response type is not a packet-response: ", {payload[0]})
        return not ok

    if payload[2] != STATUS_S.rstrip():
        print("The last packet was not successfull ->", payload[2])
        return not ok

    print(f"Server confirmed that the packet {payload[1]} has a status  of \"{payload[2]}\" ")
    print(f"And has received {payload[3]} packets, expecting the next packet to have a tag of {payload[4]}")

    return ok


enc_data = send_packet_status()
verify_packet_status(enc_data)
