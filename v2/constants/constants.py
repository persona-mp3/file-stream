import struct 

"""
Contains all information about status codes, request types and enoded formats
"""

# =============================================================================================
# DIFFERENT RESPONSE TYPES AND THEIR STATUS CODE
#
# Ack-Request and Ack-Responses have status codes of 200 and 400 representing success and failure
# The '200', '400' status codes are also used in Packet-Status responses sent by the server
#
# Operational response is used to represent exceptions that have occured in the server itself, and bears
# a status code of '500'. This is solely to be used in where Exceptions might occur
#
# Packet-Status represents the state of each packet recieved by the server. It bears 200 and 400
#
# Malformed-Packet bears a '401' code. Used when decoding a packet from the client.
#
# =============================================================================================
# BINARY FRAMING
# All Request types have their length-encoded into a single byte, which means 0 - 255 digits can be represented. 
#
#
#
# =============================================================================================

VERSION_1 = "001"
VERSION_2 = "002"

VERSIONS = {VERSION_1, VERSION_2}

HEADER = 4  # first 4-bytes of content-length for binary serialised protocols
PORT = 6000
HOST = "0.0.0.0"

FORMAT = "utf-8"  # encoding format is utf-8

ENC_VERSION_2 = VERSION_2.encode(FORMAT)
VERSION_LEN = struct.pack("B", len(ENC_VERSION_2))

# all constants with 'ack' prepended mainly refers to Ack-Request-Response
ACK_VERSION_2 = f"{VERSION_2} \r\n".encode(FORMAT)
ACK_REQ = "Acknowledge"
ACK_RES = "Acknowledged"
ACK_S = "200"  
ACK_F = "400" 
ENC_ACK_REQ = f"{ACK_REQ} \r\n".encode(FORMAT)
ENC_ACK_RES = f"{ACK_RES} \r\n".encode(FORMAT)
ENC_ACK_S = ACK_S.encode(FORMAT)
ENC_ACK_F = ACK_F.encode(FORMAT)

# ============= PACKET-REQ-RES ==========================
PACKET_REQ = "Packet"
PACKET_RES = "Packet-Status"
ENC_PACKET_REQ: bytes = PACKET_REQ.encode(FORMAT)
ENC_PACKET_REQ_LEN: bytes = struct.pack("B", len(ENC_PACKET_REQ))
ENC_PACKET_RES: bytes = PACKET_RES.encode(FORMAT)
ENC_PACKET_RES_LEN: bytes = struct.pack("B", len(ENC_PACKET_RES))

# ============= OPERATIONAL-RESPONSE ==========================
OPP_RES = "Operational"  
OPP_CODE = "500"
ENC_OPP_RES: bytes = OPP_RES.encode(FORMAT)
ENC_OPP_RES_LEN: bytes = struct.pack("B", len(ENC_OPP_RES))

# ============= MALFORMED-RESPONSE ==========================
MALF_RES = "Malformed-Packet"  
MALF_CODE = "401"
ENC_MALF_RES: bytes = MALF_RES.encode(FORMAT)
ENC_MALF_RES_LEN: bytes = struct.pack("B", len(ENC_MALF_RES))


# ============= CORRUPTED-RESPONSE ==========================
CORRUPTED_RES = "Corrupted"  
CORRUPTED_CODE = "399"
ENC_CORRUPTED_RES = CORRUPTED_RES.encode(FORMAT)
ENC_CORRUPTED_RES_LEN: bytes = struct.pack("B", len(ENC_CORRUPTED_RES))


# ============= DISCONNECT REQUEST ==========================
DISCONN_REQ = "Disconnect"
DISCONN_CODE = "000"
ENC_DISCONN_REQ = DISCONN_REQ.encode(FORMAT)
ENC_DISCONN_LEN = struct.pack("B", len(ENC_DISCONN_REQ))

# ============= UNSUPPORTED RESPONSE ==========================
UNSUPPORTED_RES = "Unsupported"
UNSUPPORTED_CODE = "444"
ENC_UNSUPPORTED_RES = UNSUPPORTED_RES.encode(FORMAT)
ENC_UNSUPPORTED_LEN = struct.pack("B", len(ENC_DISCONN_REQ))


SUPPORTED_REQ_RES = {ACK_RES, ACK_REQ, OPP_RES, MALF_RES, PACKET_REQ, PACKET_RES, DISCONN_REQ}
# ========== BASE BODY ===== 
