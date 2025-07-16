import sys 
import os 
from client import streamer


def read_args() -> None:
    args = sys.argv
    if len(args) < 2:
        print("no arguments passed in")
        exit()
    files = args[1:]
    for file in files:
        streamer(file)


# read_args()
# def mkdirs(path_name: str) -> None:
#     isFolder = path_name.contains("/")
#     file_name = path_name
#     folder_name = ""
#     if isFolder:
#         folder_stuct = path_name.split("/")
#         file_name = folder_struct[1]
#         folder_name = folder_struct[0]
#     pass
