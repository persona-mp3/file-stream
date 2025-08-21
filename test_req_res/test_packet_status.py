import struct
from v2.responses import response as res


def manual_packet_stats(tag: int, recvd: int, retry: bool) -> bytes:
    enc_tag = f"{tag}".encode(res.FORMAT)
    enc_recvd = f"{recvd}".encode(res.FORMAT)
    tag_len = struct.pack("B", len(enc_tag))
    recvd_len = struct.pack("B", len(enc_recvd))
    enc_expected = f"{tag + 1}".encode(res.FORMAT)
    expected_len = struct.pack("B", len(enc_expected))

    BASE_BODY = res.VERSION_LEN + res.ENC_VERSION_2
    body = None

    if retry:
        print("sending retry response")
        body = (
            res.ENC_RETRY_RES_LEN + res.ENC_RETRY_RES +
            struct.pack("B", len(res.RETRY_CODE.encode(res.FORMAT))) +
            res.RETRY_CODE.encode(res.FORMAT) +
            tag_len + enc_tag + recvd_len + enc_recvd + tag_len + enc_tag
        )
    else:
        print("sending 200 for packet-status")
        body = (
            res.ENC_PACKET_RES_LEN + res.ENC_PACKET_RES +
            struct.pack("B", len(res.ACK_S.encode(res.FORMAT))) +
            res.ACK_S.encode(res.FORMAT) +
            tag_len + enc_tag + recvd_len + enc_recvd + expected_len + enc_expected
        )

    if body is None:
        print("Why is body still None>>??")
        exit(1)

    payload = BASE_BODY + body
    header = struct.pack("!I", len(payload))
    response = header + payload
    return response


def test_packet_stats_response() -> None:
    tag = 1
    recvd = 1
    retry = False
    assert res.packet_stats2(tag, recvd, retry) == manual_packet_stats(tag, recvd, retry)


def test_packet_stats_response_retry() -> None:
    tag = 1
    recvd = 1
    retry = True
    # when caller decides to ask for a packet-retrial
    assert res.packet_stats2(tag, recvd, retry) == manual_packet_stats(tag, recvd, retry)
