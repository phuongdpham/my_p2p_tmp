import socket
import pickle
from _thread import *
import time

s = socket.socket()
host = socket.gethostname()
port = 7777
s.bind((host, port))

s.listen(5)


def client_thread(conn, addr):
    time.sleep(3)
    conn.send(bytes('Thank you for connecting', 'utf-8'))
    print('Got connection from ', addr)

    while True:
        try:
            data = pickle.loads(conn.recv(1024))
            print(data)
        except EOFError:
            break

    conn.close()


print('Server is running...')

while True:
    c, addr = s.accept()
    start_new_thread(client_thread, (c, addr))
s.close()