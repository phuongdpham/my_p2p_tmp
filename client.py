import socket
import time
import multiprocessing.connection

import os

homedir = os.path.expanduser('~')
path = homedir + '/test/'

files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]  # and not f.startswith('.')]

host = socket.gethostname()
port = 7777

# sock = socket.socket()
# sock.connect((host, port))

client = multiprocessing.connection.Client((host, port))

mess = client.recv()
print(mess)


while True:
    print('waiting...')
    try:
        client.send(files)
        data = client.recv()

        print(data)
        # print(client)
    except EOFError as err:
        break
    except OSError:
        print('Disconnected')
        break
    except TimeoutError as err:
        print(err)
        break

client.close()
