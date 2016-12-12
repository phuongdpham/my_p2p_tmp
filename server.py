import socket
import pickle
from _thread import *
import time
import multiprocessing.connection

# s = socket.socket()
host = socket.gethostname()
port = 7777
# s.bind((host, port))

# s.listen(5)

i = 0
conn = None


def client_thread():
    global i

    # print('Got connection from ', addr)

    while True:
        try:
            time.sleep(3)
            conn.send('Thank you for connecting')
            i += 1
            if i == 3:
                conn.close()
                break
        except EOFError:
            break

    conn.close()


print('Server is running...')
s = multiprocessing.connection.Listener((host, port))

while True:
    print('Listening...')
    conn = s.accept()

    print('Got connection from ', conn.fileno())
    conn.send(['Thank you for connecting', 'abcc'])

    try:
        while True:
            try:
                files = conn.recv()
                print(files)
                time.sleep(3)
                conn.send([files, ])
            except EOFError:
                print('Connection disconnected!')
                break
            except OSError as err:
                print(err)
                break
        conn.close()
    except BrokenPipeError as err:
        print(err)

s.close()