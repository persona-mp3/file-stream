import time
import struct 
import hashlib

FORMAT = "utf-8"
RETRY_REQ = "Retrial"
ENC_RETRY = f"{RETRY_REQ} \r\n".encode(FORMAT)


def retry_request(author: str, filesum: str, packet_id: int, data: bytes) -> bytes:
    """The data is not necessarily used in this process, and this packet_id 
    must be the one before the last one sent that did not make it, just to make 
    things easier, because on the server, maybe even before the client could send the whole packet 
    mid transfer, might have disconnected, so we rely on the previous one. Kind of 
    like a puzzle peice

    Structure:
        (4B packet-size)(version)(cwd)
        (author)(filesum)(tag)(datasum)
    """
    if author is None or packet_id is None:
        print("[fatal]: packet_id or author must not be none")

    cksum = hashlib.sha256(data).hexdigest()
    cksum = f"{cksum} \r\n".encode(FORMAT)

    filesum = f"{filesum} \r\n".encode(FORMAT)
    enc_author = f"{author} \r\n".encode(FORMAT)
    enc_tag = (str(packet_id) + " \r\n").encode(FORMAT)

    version = "002 \r\n".encode(FORMAT)

    payload = (
        version + ENC_RETRY +
        enc_author + filesum + 
        enc_tag + cksum
    )
    header = struct.pack("!I", len(payload))

    request = header + payload
    return request


def retry_response(request: bytes, filesum: str, data: bytes) -> None:
    print("parsing request....")
    payload = request[4:]  # reading from the first 4bytes to get the payload
    cksum = hashlib.sha256(data).hexdigest()

    logs = {
        "author": "main.go",
        "packet_id": "12",
        "filesum": filesum, 
        "cksum": cksum, 
    }

    fields = [field for field in payload.decode(FORMAT).split(" \r\n") if field.strip()]
    auth_data = tuple(fields[2:])
    print("request-fields ->\n", auth_data)

    for ks in logs:
        if logs[ks] in auth_data:
            continue
        else:
            print("these don't match??")
            print(ks, logs[ks])
            return False
            break

    print("All matches passed")
    # begin protcol??, since we already have the file_created, we can just continue appending to it. 
    # If any of these matches differ, we direct the client to make a new Ack-Request


def main():
    file_name = "main.go"
    packet_id = 12 
    file_sum = hashlib.sha256(file_name.encode(FORMAT)).hexdigest()
    data = "Just when you think you're done, you got 5 more reps".encode(FORMAT)

    request = retry_request(file_name, file_sum, packet_id, data)
    print()
    print("simulating retrial")
    time.sleep(0.6)
    _ = retry_response(request, file_sum, data)


if __name__ == "__main__":
    main()
