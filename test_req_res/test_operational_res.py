import struct
from v2.responses import response as res


def manual_operational() -> bytes:
    payload = (
        res.VERSION_LEN + res.ENC_VERSION_2 + res.ENC_OPP_RES_LEN +
        res.ENC_OPP_RES + struct.pack("B", len(res.OPP_CODE.encode(res.FORMAT))) + res.OPP_CODE.encode(res.FORMAT)
    )
    header = struct.pack("!I", len(payload))

    response = header + payload
    return response


def test_operational_res() -> None:
    assert res.operational_response() == manual_operational()
