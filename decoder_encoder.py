import struct
from utils.utils import file_handler


def create_header() -> bytearray:
    req_type = "GitHubCopilot".encode("utf-8")
    req_len = struct.pack("B", len(req_type))

    FORMAT = "utf-8"

    # we are parsing it into string so we can know encode the length of the tag and read from later on 
    tag = str(12).encode("utf-8")
    enc_tag_len = struct.pack("!I", len(tag))

    sent = str(1002).encode(FORMAT)
    enc_sent_len = struct.pack("!I", len(sent))

    # data = "Trash the ploy, turn myself into posterboy\r\nLive by the sword make myself turn 2 to 4"
    file = open("BinarySearch.java", "r")
    content = file.readlines()
    content = "".join(content)
    enc_data = content.encode(FORMAT)

    # so we need to know the request type, what number this packet is and get data
    # since we always know that the req_type will be packed into 1byte, we dont need to start encoding the length# 
    body = req_len + req_type + enc_sent_len + sent + enc_tag_len + tag + enc_data
    header = struct.pack("!I", len(body))

    packet = header + body

    return packet


def decode_header():
    # so we know the following: 
    """
    content-len > read first 4bytes
    req-type > read the next byte, decode that and read [5: decoded-len+5] and then decode the type
    enc-len > is after the req-type so we are starting from ?? the req_type which is decoded-len+5 and reading the next 4bytes, 
    enc-len = data[decoded-len + 5: decoded-len + 10]
    """

    encoded_data = create_header()
    content_len = struct.unpack("!I", encoded_data[:4])[0]
    print(f"decoded content_len -> {content_len}")

    req_type_len = struct.unpack("B", encoded_data[4: 5])[0]
    print(f"decoded req-type-length -> {req_type_len}")
    req_type = encoded_data[5: req_type_len + 5]
    print(f"decoded req_type : {req_type}")

    sent_len = struct.unpack("!I", encoded_data[req_type_len + 5: req_type_len + 5 + 4])[0]
    # print(f"sent_len: {sent_len} so we are to start from req_type_len+ 5 + 4 to {sent_len} plus whats before")

    client_sent = encoded_data[req_type_len + 9: req_type_len + 9 + sent_len]
    print(f"client sent this amount of packets already -> {client_sent}")

    tag_len = struct.unpack("!I", encoded_data[req_type_len + 9 + sent_len: req_type_len + 9 + sent_len + 4])[0]
    print("tag_len", tag_len)
    tag = encoded_data[req_type_len + 13 + sent_len: tag_len + req_type_len + 13 + sent_len]
    print(f"is this correct tag passed in?: {tag}")

    data = encoded_data[tag_len + req_type_len + 13 + sent_len:]
    print("actual data -~> \n", data.decode("utf-8"))


# decode_header()


def decode_packet(packet: bytes):
    # so we know the following: 
    """
    content-len > read first 4bytes
    req-type > read the next byte, decode that and read [5: decoded-len+5] and then decode the type
    enc-len > is after the req-type so we are starting from ?? the req_type which is decoded-len+5 and reading the next 4bytes, 
    enc-len = data[decoded-len + 5: decoded-len + 10]
    """

    encoded_data = packet
    content_len = struct.unpack("!I", encoded_data[:4])[0]
    # print(f"decoded content_len -> {content_len}")

    req_type_len = struct.unpack("B", encoded_data[4: 5])[0]
    # print(f"decoded req-type-length -> {req_type_len}")
    req_type = encoded_data[5: req_type_len + 5]
    # print(f"decoded req_type : {req_type}")

    sent_len = struct.unpack("!I", encoded_data[req_type_len + 5: req_type_len + 5 + 4])[0]
    # print(f"sent_len: {sent_len} so we are to start from req_type_len+ 5 + 4 to {sent_len} plus whats before")

    client_sent = encoded_data[req_type_len + 9: req_type_len + 9 + sent_len]
    print(f"client sent this amount of packets already -> {client_sent}")

    tag_len = struct.unpack("!I", encoded_data[req_type_len + 9 + sent_len: req_type_len + 9 + sent_len + 4])[0]
    # print("tag_len", tag_len)
    tag = encoded_data[req_type_len + 13 + sent_len: tag_len + req_type_len + 13 + sent_len]
    # print(f"is this correct tag passed in?: {tag}")

    data = encoded_data[tag_len + req_type_len + 13 + sent_len:]
    # print("actual data -~> \n", data.decode("utf-8"))
    print(data.decode("utf-8"))
    print(f"\n\n === \ns - last packet sent had a tag of -> {tag}\n\n === \n")
    print(f"\n\n === \ns - packet-tag {tag}, size {content_len}\n\n === \n")


def create_data_packet(fname: str) -> None:
    req_type = "Packet".encode("utf-8")
    req_len = struct.pack("B", len(req_type))

    FORMAT = "utf-8"

    file = file_handler(fname, "rb")
    packet_sync = 0 

    CHUNK_SIZE = 1024
    chunks = []
    while True:
        chunk = file.read(CHUNK_SIZE)
        if not chunk:
            print("no more content to read from file, closing file")
            file.close()
            break
        chunks.append(chunk)

    N_PACKETS = len(chunks)
    print("total packets to send:", N_PACKETS)

    while packet_sync < N_PACKETS:
        tag = str(packet_sync).encode(FORMAT)
        sent = str(packet_sync).encode(FORMAT)

        enc_tag_len = struct.pack("!I", len(tag))
        enc_sent_len = struct.pack("!I", len(sent))

        body = req_len + req_type + enc_sent_len + sent + enc_tag_len + tag + chunks[packet_sync]
        header = struct.pack("!I", len(body))

        packet = header + body

        decode_packet(packet)
        # print(f"packets-sent: {sent}")

        packet_sync += 1


create_data_packet("rengoku")
