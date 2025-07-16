import sys 
from client import streamer


def read_args() -> None:
    args = sys.argv
    if len(args) < 2:
        print("no arguments passed in")
        exit()
    files = args[1:]
    for file in files:
        streamer(file)


read_args()
