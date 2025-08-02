import struct 


VERSION = "001"

FORMAT = "utf-8"
ACK_REQ = "Acknowledge"
ACK_S = "200"
ACK_F = "400"
ACK_ER = "500"

OPP_RES = "Operation"

PACKET_REQ = "Packet"
PACKET_RES = "Packet-Status"

ENC_PACKET_REQ: bytes = PACKET_REQ.encode(FORMAT)

HOST = "0.0.0.0"

ENC_ACK_VERSION: bytes = (VERSION + " \r\n").encode(FORMAT)
ENC_ACK_VERSION_LEN: bytes = struct.pack("B", len(ENC_ACK_VERSION))  

ENC_ACK_REQ: bytes = (ACK_REQ + " \r\n").encode(FORMAT)
ENC_ACK_S: bytes = (ACK_S + " \r\n").encode(FORMAT)
ENC_ACK_F: bytes = (ACK_F + " \r\n").encode(FORMAT)

ENC_ER: bytes = ACK_ER.encode(FORMAT)
ENC_ER_LEN: bytes = struct.pack("B", len(ENC_ER))


ENC_VERSION: bytes = VERSION.encode(FORMAT)
ENC_VERSION_LEN: bytes = struct.pack("B", len(ENC_VERSION))

ENC_OPP_RES: bytes = VERSION.encode(FORMAT)
ENC_OPP_LEN: bytes = struct.pack("B", len(ENC_OPP_RES))


BASE_BODY: bytes = ENC_VERSION_LEN + ENC_VERSION 


def error_response() -> bytes:
    """
    Returns encoded error response with status code of 500. This is sent when Exceptions occur in the program or 
    operations like calling an external API or IO Operations. The client can decide what to do but the Caller has to 
    close the connection to the client. 

    Response structure: 
        version-len + version + response-type-len + response-type +  status-code: 500

    Returns:
        Encoded packet response for error_code 500
    """
    body: bytes = BASE_BODY + ENC_OPP_LEN + ENC_OPP_RES + ENC_ER
    header: bytes = struct.pack("!I", len(body))

    err_response: bytes = header + body
    return err_response
