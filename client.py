import socket
import time

host = socket.gethostname()
port = 7777

sock = socket.socket()
sock.connect((host, port))


while True:
    print('waiting...')
    try:
        data = sock.recv(1024)
        print(data.decode())
        print(sock.getpeername(), sock.getsockname()[1])
    except OSError or EOFError:
        print('Disconnected')
        break

sock.close()