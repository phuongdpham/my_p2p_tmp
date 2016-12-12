import socket
import time
from multiprocessing.connection import Listener

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
    except TimeoutError as err:
        print(err)
        break

sock.close()
