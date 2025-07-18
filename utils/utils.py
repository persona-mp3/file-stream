import socket 
from typing import Union, IO


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
        exit()


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
        exit()
