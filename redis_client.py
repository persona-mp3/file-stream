import redis 

r = redis.Redis(host="localhost", port=6380, decode_responses=True)


def mock_data():

    print("setting mock data")
    r.hset("new-uuid-session", mapping={
        "author": "main.go",
        "cwd": "wsl-prt",
        "file_cksum": "file-cksum",
        "packet_id": 12,
        "data-cksum": "data-cksum",
        "n_packets": 20
    })


def validate_client(session_id: str):
    mock_data()
    try:
        print(f"Contacting redis for {session_id}...")

        return r.hgetall(session_id)
    except Exception as e:
        print("Damn...")
        print(e)
