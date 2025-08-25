import os 
from pathlib import Path 
import re 
import socket 
import struct
from typing import Union, IO
from v2.constants.constants import (MAX_PAYLOAD)

HEADER = 4  # content-length to read from client data


class MaxPayload(Exception):
    """
    Used when a client tries to send a huge ton 
    of data over the connection, potenitally to DDOS.
    The connection should be dropped instantly. 
    """
    pass


def create_client(ADDR: Union[str, int]) -> socket:
    """
    Creates a client socket and connects to ADDR, a tuple of (IP_ADDR, PORT)
    Raises an exception and exits if any error occurs, and returns connected socket if successful
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.connect(ADDR)
        return s
    except Exception as e:
        print(f"An error occured in creating client socket:\n{e}")


def file_handler(file_name: str, flag: str = "r") -> IO:
    """
    Opens file for readind by defaut and returns file object. 
    Raises an exception and exits code if an error occurs
    """
    try:
        file = open(file_name, flag)
        return file
    except Exception as e:
        print(f"An error occured in file opeation:\n{e}")


def find_parent(file_path: str) -> tuple[str, str]:
    """
    Implements pythons regex to find all occurences of "/" inside the file_path. 
    It takes a string/file_path in this case, to find all it's nested parent directories
    returning both of them as seperate strings.

    Callers:
        Typically called by recv_data() in server

    Returns:
        tuple(nested_folder, nested_file)

    """

    print("\n\n === finding parent === \n\n")
    positions: list = []

    # The finditer(substr, str) recursively searches a string against the substr. 
    # it returns the position at where it occurs and stops. Using /user20/home/documents as an example.
    # Using finditer("/", str) will return 0,1 for the first occurence of "/", return 6,7 for second and so on
    # This is gotten by calling m.start() and m.end() on the iterator type returned by re.finditer()
    # And depending on how long file_path is ,in this use-case, we know that the last-item is the nested file 
    # and all others before are it's parents.

    for m in re.finditer("/", file_path):
        positions.append(m.end())

    nested_folders = file_path[:positions[-1]]
    file = file_path[positions[-1]:]
    return (nested_folders, file)


def create_parents(CWD: str, nested_folder: str, file: str) -> Path:
    """
    Creates the nested directories in the CWD gotten from the ACK-Header

    The Caller is responsible to appending the file to the end of the returned Path object. 
    And is readily available for reading and writing ie Path.write_text()...

    Returns:
        - Appended path to the expected file
    """

    # to make sure that the files and folders are made inside the users own folder on the machine 
    base_path = os.path.join(CWD, nested_folder)
    try:
        os.makedirs(base_path, mode=0o777, exist_ok=True)
        full_path = Path.cwd() / base_path / file
        print(f"Path to nested_folder, {full_path}")
        return full_path 
    except Exception as e:
        print(repr(e))


def get_all_files() -> list[str]:
    """
    Gets all files in current directory recursively including nested folders.
    Ignores the script itself and .git folder

    Returns:
        - List of files 
    """
    CWD = Path.cwd()
    ready_files = []
    IGNORE_FILES = {"__pycache__", ".pytest_cache", "node_modules", "package-lock.json", "client", "client.py", ".ssid", "logs.txt"}
    IGNORE_EXTENSIONS = {".png", ".jpg", ".log"}

    for file in CWD.rglob("*"):
        if (
            ".git" not in file.parts and
            not any(part in IGNORE_FILES for part in file.parts) and
            not any(part in IGNORE_EXTENSIONS for part in file.parts) and
            file.is_file()
        ):
            ready_files.append(str(file.relative_to(CWD)))

    return ready_files


def get_payload(s: socket.socket) -> bytes:
    """
    Takes a socket object and gets the data of the payload. It does not handle slicing of data 
    it only reads it's content from the client provided the first 4-bytes is expected as the content-length or the socket has not 
    been closed. It is the responsibility of the Caller to handle the data or check it

    Rasies an Exception if an invalid argument is provided or and error occured in socket operation, typically a BadSocketDescriptor

    Reuturns:
        payload in bytes
    """
    if not isinstance(s, socket.socket):
        raise ValueError("Expected socket.socket, got", type(s))

    try:
        content_len: bytes = b''
        while len(content_len) < HEADER:
            chunk = s.recv(HEADER - len(content_len))
            content_len += chunk

        content_len: int = struct.unpack("!I", content_len)[0]

        payload: bytes = b''
        while len(payload) < content_len:
            chunk = s.recv(content_len - len(payload))
            payload += chunk

        return payload
    except Exception as e:
        print("An error occured in getting content-length from the socket provided", e)


def recv_payload(s: socket.socket) -> bytes | None:
    if not isinstance(s, socket.socket):
        raise ValueError("Expected type of socket.socket, got:", type(s))
        return

    try: 
        content_len = b''
        while len(content_len) < HEADER:
            chunk = s.recv(HEADER - len(content_len))
            content_len += chunk

        content_len = struct.unpack("!I", content_len)[0]

        if content_len > MAX_PAYLOAD:
            raise MaxPayload(f"Client has sent too much data of size {content_len}")
        # extracting payload
        payload = b''
        while len(payload) < content_len:
            chunk = s.recv(content_len - len(payload))
            payload += chunk

        return payload
    except ConnectionResetError:
        print("Connection has been disconnected")
        return
    except Exception as e:
        print("An unexpected error occured in utils.recv_payload\n:", e)
        return


def reader(file_name: str) -> list[bytes]:
    CHUNK = 2000
    try:
        content: list[bytes] = []
        with open(file_name, "rb") as f:
            while True:
                chunk = f.read(CHUNK)
                if not chunk:
                    break
                content.append(chunk)
        return content
    except Exception as e:
        print(f"Unexpected error occcured in trying to read: {file_name}:\n {e}")
