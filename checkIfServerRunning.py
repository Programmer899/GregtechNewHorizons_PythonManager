import socket

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = sock.connect_ex(('localhost', port))
    sock.close()
    return res == 0

print(check_port(25565))