import struct 
import hashlib

from v2.logger.logger import create_logger
from v2.constants.constants import (
    ENC_VERSION_2, VERSION_LEN, FORMAT, 
    ENC_PACKET_REQ, ENC_PACKET_REQ_LEN,
)


logger = create_logger()


def encoder(tag: int, sent: int, data: bytes) -> bytes:
    """Encodes data of type ```bytes``` to create a packet.

    The ```tag``` and ```sent``` parameters are used to identify the packet on the server 
    for piecing data packets and the ```sent``` is used to sync with server in case of errors.

    The packet is pre-prended with a  ```content-length``` or ```header``` that the server uses
    to read a whole packet. Every other field has its length following it before the field 
    starting with version-length, version, request-length, request-type tag-length, tag and so on

    A sha256-hash, ```checksum``` of the ```data``` is also taken and appended to the packet

    Structure:
        (4B content-length) (1B version-length)(version)
        (1B request-length) (request-type)
        (1B sent-length)(sent) (1B tag-length)(tag) 
        (1B hash-length)(sha256 hash)
        (data)

    Returns:
        Fully encoded packet
    """
    if not isinstance(data, bytes):
        logger.error(f"Expected data of type bytes, got: {type(data)}")
        raise ValueError(f"Expected data of type bytes, got: {type(data)}")
        return b''

    if not isinstance(tag, int):
        logger.error(f"Expected tag of type int, got: {type(tag)}")
        raise ValueError(f"Expected tag of type int, got: {type(tag)}")
        return b''

    if not isinstance(sent, int):
        logger.error(f"Expected sent of type int, got: {type(sent)}")
        raise ValueError("Expected sent of type int, got: {type(sent)}")
        return b''

    enc_tag = str(tag).encode(FORMAT)
    enc_sent = str(sent).encode(FORMAT)
    enc_tag_len = struct.pack("!I", len(enc_tag))
    enc_sent_len = struct.pack("!I", len(enc_sent))

    checksum = hashlib.sha256(data).hexdigest().encode(FORMAT)
    checksum_len = struct.pack("B", len(checksum))

    payload = (
        VERSION_LEN + ENC_VERSION_2 +
        ENC_PACKET_REQ_LEN + ENC_PACKET_REQ +
        enc_sent_len + enc_sent + enc_tag_len + enc_tag +
        checksum_len + checksum + data
    )

    header = struct.pack("!I", len(payload))
    packet = header + payload
    logger.info("Packet of succesfully encoded")
    return packet


if __name__ == "__main__":
    print("Encoder script is used to encode data. This is not supposed to be ran as a script but as a module")
