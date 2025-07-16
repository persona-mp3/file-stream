import sys 



def read_args() -> None:
    args = sys.argv
    if len(args) < 2:
        print("no arguments passed in")
        exit()
    files = args[1:]
    print(f"files to send to server, confirm? {files}")

read_args()
