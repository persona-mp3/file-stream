from v2.protocol import encoder as enc
from v2.protocol import decoder as dec
from v2.constants.constants import (FORMAT, VERSION_2, PACKET_REQ)


# Integration testing for encoder and decoder moules for basic encoding and decoding
def test_protocol_modules():
    data = "The Joe Rogan Podcast".encode(FORMAT)
    encoded_packet = enc.encoder(0, 0, data)
    decoded_packet = dec.decoder(encoded_packet[4:])

    expected_data = (VERSION_2, PACKET_REQ, "0", "0", data.decode(FORMAT))
    assert decoded_packet == expected_data
