import sys 
import os 
from client import streamer
from utils.utils import file_handler


def read_args() -> None:
    args = sys.argv
    if len(args) < 2:
        print("no arguments passed in")
        exit()
    files = args[1:]
    print(os.path.basename(os.getcwd()))


read_args()


def isDir(fname) -> list:
    ff = []
    if "/" in fname:
        ff.append(fname.split("/"))
    else:
        # ff.append(fname)
        return fname

    path_struct = "/".join(ff[0])
    # print(path_struct)

    return path_struct


def mm(fname):
    file_path = isDir(fname)
    print("creating ", file_path)
    if "/" in file_path: 
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        except Exception as e:
            print(f"An error occured in making sub_dirs for {file_path}: {e}")

    f = file_handler(file_path, "a")
    f.write("BOMBORASCLAT\n Watching Patheon")
    f.close()


a = "rengoku2/kol1/rai.js"
b = "tanjiro"


# mm(b)
# mm(b)
