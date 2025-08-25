import struct 
import hashlib
from typing import NamedTuple

from v2.logger.logger import create_logger
from v2.constants.constants import (
    VERSION_1, VERSION_2,
    FORMAT, PACKET_REQ, DISCONN_REQ
)


# Used for checking future and past versions when decoding
VERSIONS = {VERSION_1, VERSION_2}
REQUESTS = {PACKET_REQ, DISCONN_REQ}


logger = create_logger()


class PacketInfo(NamedTuple):
    version: str
    request_type: str
    sent_packets: str
    packet_tag: str
    data: str


class DecoderError(Exception):
    """Raises when a packet is malformed. 
    ```Malformed``` response should be sent to the client"""
    pass


class UnsupportedError(Exception):
    """Raises when a client sends an unsupported version, or request.
    ```Unsupported``` response should be sent to the client.
    """
    pass


class CorruptionError(Exception):
    """
    Raises when the clients checksum for data does not match our built version 
    packet is malformed. ```Corrupted``` response should be sent to the client
    """
    pass


class SupportedDisconnect(Exception):
    """Used to alert when client sends a ```Disconnect``` request"""
    pass


def decoder(packet: bytes) -> PacketInfo:
    """
    Decodes the packet recieved from the client, and is mainly used for the ```Packet``` Request. 
    The parameter ```packet``` must first be derived from the Caller unless raises a Struct Error

    Checksum and Version validation is done. Any Exception raised must send an ```Malformed```
    response to the client. Same for other failed validations except for checksum as it would require
    a ```Corrupted``` response.

    If valid_packet is False, all other fields will be empty

    Returns:
    (version, request_type, sent_packets, packet_tag, data)
    """

    if not isinstance(packet, bytes):
        raise ValueError(f"Expected type of bytes, got, {type(packet)}")

    offset = 0 
    version_len = packet[offset: offset + 1]
    offset += 1

    try:
        # === 1. Decoding version === 
        version_len = struct.unpack("B", version_len)[0]
        version = packet[offset: offset + version_len].decode(FORMAT)
        offset += version_len

        if version not in VERSIONS:
            logger.info(f"Unsupported version: {version}, sending unsupported response")
            raise UnsupportedError(f"Version type not supported, Got: {version}")

        # === 2. Decoding request-type === 
        request_len = packet[offset: offset + 1]
        offset += 1 
        request_len = struct.unpack("B", request_len)[0]
        request_type = packet[offset: offset + request_len].decode(FORMAT)
        offset += request_len

        if request_type not in REQUESTS:
            logger.info(f"Unsupported request-type: {request_type}, sending Unsupported")
            raise UnsupportedError(f"Request type not supported, Got: {request_type}")
        elif (request_type == DISCONN_REQ):
            logger.info("Client initiating close")
            raise SupportedDisconnect("Closing connection")

            # === 3. Decoding sent packets === 
        sent_packets_len = packet[offset: offset + 4]
        if len(sent_packets_len) != 4:
            logger.warn(f"Error occured in extracting sent_packets_len. Expected 4 got: {sent_packets_len}")
            raise DecoderError(f"Error occured in extracting sent_packets_len. Expected 4 got: {sent_packets_len}")

        offset += 4
        sent_packets_len = struct.unpack("!I", sent_packets_len)[0]
        sent_packets = packet[offset: offset + sent_packets_len].decode(FORMAT)
        offset += sent_packets_len
        logger.debug(f"Sent Packets: {sent_packets}")

        # === 4. Decoding tag === 
        packet_tag_len = packet[offset: offset + 4]
        if len(packet_tag_len) != 4:
            logger.warn(f"Error occured in extracting packet_tag_len. Expected 4 got: {packet_tag_len}")
            raise DecoderError(f"Error occured in extracting packet_tag_len. Expected 4 got: {packet_tag_len}")

        offset += 4
        packet_tag_len = struct.unpack("!I", packet_tag_len)[0]
        packet_tag = packet[offset: offset + packet_tag_len].decode(FORMAT)
        offset += packet_tag_len
        logger.debug(f"Packet-Tag: {packet_tag}")

        # === 5. Extracting sha256 checksum === 
        checksum_len = packet[offset: offset + 1]
        offset += 1
        checksum_len = struct.unpack("B", checksum_len)[0]
        checksum = packet[offset: offset + checksum_len].decode(FORMAT)
        offset += checksum_len

        # === 6. Data === 
        data = packet[offset:]
        build_checksum = hashlib.sha256(data).hexdigest()

        # === 7. Validating checksum === 
        if checksum != build_checksum:
            logger.info("Client checksum and built checksum are not the same")
            raise CorruptionError("Client checksum and built checksum are not the same")

        logger.info("Client packet decoded successfully")
        return PacketInfo(version, request_type, sent_packets, packet_tag, data.decode(FORMAT))

    except struct.error as err:
        print(f"[CRITICIAL]: Error occured in decoding data:\n {err}")
        logger.warn("Error in decoding entire packet")
        return PacketInfo("", "", "", "", "")
