import os 
from pathlib import Path 
import re 
import socket 
from typing import Union, IO

def create_client(ADDR: tuple) -> socket:
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


def find_parent(filePath: str) -> tuple:
    """
    Implements pythons regex to find all occurences of "/" inside the filePath. 

    Depending on how much "/" the filePath contains, all occurences of "/" will vary hence using "-1"
    The last occurence is where the file is and everything before that are parent directories


    Returns:
        - Tuple of nested folder and the nested file

    """

    print("\n\n === finding parent === \n\n")
    positions: list = []

    for m in re.finditer("/", filePath):
        positions.append(m.end())

    nested_folders = filePath[:positions[-1]]
    file = filePath[positions[-1]:]

    print(f"Nested_Folder {nested_folders}, File: {file}")

    return (nested_folders, file)


def create_nested(CWD: str, nested_folder: str, file: str) -> Path:
    """
    Creates the nested directories in the CWD gotten from the ACK-Header

    The Caller is responsible to appending the file to the end of the returned Path object. 
    And is readily available for reading and writing ie Path.write_text()...

    Returns:
        - Appended path to the expected file
    """
    print("\n\n === creating nested directories === \n\n")

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
    IGNORE_FILES = {"__pycache__", ".pytest_cache", "node_modules", "package-lock.json", "client", "client.py"}
    IGNORE_EXTENSIONS = {".png", ".jpg"}

    for file in CWD.rglob("*"):
        if (
            ".git" not in file.parts 
            # and (file not in ignore_files)
            and not any(part in IGNORE_FILES for part in file.parts)
            and not any(part in IGNORE_EXTENSIONS for part in file.parts)
            and file.is_file()
        ):
            ready_files.append(str(file.relative_to(CWD)))

    print("Files ready...")
    return ready_files


def file_handler(fname: str, flag="r") -> IO:
    try:
        f = open(fname, flag)
        return f
    except Exception as e:
        print(f"An error occured in file_handler\n{e}")
        exit()
