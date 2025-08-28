import socket
import time

async def check_port(port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = sock.connect_ex(('localhost', port))
    sock.close()
    return res == 1

if __name__ == "__main__":
    while True:
        print(check_port(25575))
        time.sleep(.5)
