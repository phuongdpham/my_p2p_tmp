import socket
import pickle
from _thread import *
import time

s = socket.socket()
host = socket.gethostname()
port = 7777
s.bind((host, port))

s.listen(5)

i = 0


def client_thread(conn, addr):
    global i

    print('Got connection from ', addr)

    while True:
        try:
            time.sleep(3)
            conn.send(bytes('Thank you for connecting', 'utf-8'))
            i += 1
            if i == 3:
                conn.close()
                break
        except EOFError:
            break

    conn.close()


print('Server is running...')

while True:
    c, addr = s.accept()
    start_new_thread(client_thread, (c, addr))
s.close()