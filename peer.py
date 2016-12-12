import socket
import pickle
import threading
import os
import platform
import time

lock = threading.RLock()

port1 = 5555  # port number between machine 1 and 2
port2 = 6666  # port number between machine 1 and 3
port3 = 7777  # port number between machine 2 and 3

ports = [port1, port2, port3]
host = ''

# gw = os.popen("ip -4 route show default").read().split()
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect((gw[2], 0))
# host = s.getsockname()[0]
# s.close()

# host = socket.gethostname()  # local machine

machine = None

home_dir = os.path.expanduser('~')
OS = platform.system()

if OS == 'Windows':
    path = home_dir + "\\test\\"
    path.replace('\\', '/')
else:
    path = home_dir + '/test/'

if not os.path.exists(path):
    print('Create {}'.format(path))
    os.makedirs(path)
else:
    print('Exists {}'.format(path))

os.chdir(path)

my_files = []  # [[filename1, last_modified1], [filename2, last_modified2],...]
number_of_peers = 1  # number of other machine in network

threads = []
listener_socket = socket.socket()
request_socket = socket.socket()
listener_port = None
request_port = None


def load_files():
    global my_files
    my_files = []
    file_names = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.startswith('.')]

    for fn in file_names:
        # f = os.path.join(path, fn)
        stat_info = os.stat(fn)
        last_modified = stat_info.st_mtime  # os.path.getmtime(fn)
        my_files.append([fn, last_modified])


def check_last_modified(file, file_list):
    for f in file_list:
        if file[0] == f[0] and file[1] > f[1]:
            return True
    return False


def compare_with(peer_files):
    need_upd_files = []
    p_need_upd_files = []
    my_file_name_list, p_file_name_list = [], []

    for f in peer_files:
        p_file_name_list.append(f[0])

    for f in my_files:
        my_file_name_list.append(f[0])

    for f in peer_files:
        if f[0] not in my_file_name_list or check_last_modified(f, my_files):
            need_upd_files.append(f)

    for f in my_files:
        if f[0] not in p_file_name_list or check_last_modified(f, peer_files):
            p_need_upd_files.append(f)

    return need_upd_files, p_need_upd_files


def update_file(f, data):
    lock.acquire()
    try:
        # fn = os.path.join(path, f[0])
        fn = f[0]
        stat_info = os.stat(fn)
        with open(fn, 'w') as txt:
            txt.write(data)
        os.utime(fn, (stat_info.st_atime, stat_info.st_mtime))
    finally:
        lock.release()


def make_message(operator, operand):
    return [operator, operand]


def p2p_in_thread(conn, addr):
    conn.send(bytes('Thank you for connecting', 'utf-8'))  # say thank

    while True:
        try:
            data = pickle.loads(conn.recv(8096))    # wait for receive file list from peer
            if data[0] == 'EXIT':
                break
            elif data[0] == 'GET':
                load_files()
                conn.send(pickle.dumps(make_message('POST', my_files)))
            elif data[0] == 'POST':
                peer_files = data[1]
                load_files()

                print(peer_files)
                print(my_files)

                # get list of files need update from peer, and to peer
                my_need_update_files, p_need_update_files = compare_with(peer_files)

                # send request list of files need update to peer
                conn.send(pickle.dumps(make_message('POST', [my_need_update_files, p_need_update_files])))

                if my_need_update_files:
                    for my_fn in my_need_update_files:
                        d = pickle.loads(conn.recv(8096))
                        print('/> Received data file "{}" from peer {}.'.format(my_fn[0], addr))
                        update_file(my_fn, d)  # improve performance by thread later
                        conn.send(bytes('DONE', 'utf-8'))

                if p_need_update_files:
                    for fn in p_need_update_files:
                            with open(os.path.join(path, fn[0])) as txt:
                                d = txt.read()
                                try:
                                    conn.send(pickle.dumps(d))
                                except BrokenPipeError as err:
                                    print(err)
                                print('/> Sent file "{}" to peer {}.'.format(fn[0], addr))
                                confirm = conn.recv(1024)
                                print(confirm.decode())
                                del d
        except EOFError or OSError:
            print('/!\ Connection disconnected')
            conn.close()
            break


def listener_thread():
    listener_socket.listen(number_of_peers)
    while True:
        c, addr = listener_socket.accept()
        print('Got: ', addr)
        t_c = threading.Thread(target=p2p_in_thread, args=(c, addr))
        t_c.start()
        t_c.join()
        threads.append(t_c)


def request_thread():
    while True:
        print('> Load file')
        load_files()
        print('> Load file done!')

        request_socket.send(pickle.dumps(make_message('POST', my_files)))  # send to peer list of file and last modified
        try:
            data = pickle.loads(request_socket.recv(8096))  # ['POST', need_update_files, p_need_upd_files]
            my_need_update_files = data[1][1]
            p_need_update_files = data[1][0]

            if not my_need_update_files and not p_need_update_files:
                print('> Nothing to do, wait for the next change in folder...')
                time.sleep(10)
                continue

            if p_need_update_files:
                for file in p_need_update_files:
                        with open(os.path.join(path, file[0])) as txt:
                            data = txt.read()
                            request_socket.send(pickle.dumps(data))
                            print('> Sent data file "{}" to peer {}.'.format(file[0], request_socket.getpeername()))
                            confirm = request_socket.recv(1024)
                            print(confirm.decode())
                            del data

            if my_need_update_files:
                for fn in my_need_update_files:
                    d = pickle.loads(request_socket.recv(8096))
                    print('> Received data file "{}" from peer {}'.format(fn[0], request_socket.getpeername()))
                    update_file(fn, d)
                    request_socket.send(bytes('DONE', 'utf-8'))
            time.sleep(5)
        except EOFError or OSError:
            print('/!\ Connection disconnected')
            request_socket.close()
            break
        except TypeError:
            request_socket.close()
            break


def get_user_input():
    global listener_socket, host, ports

    # Set up listener thread
    while True:
        while True:
            try:
                host = input('Enter your host (IP Address): ')
                socket.inet_aton(host)
                break
            except socket.error as err:
                print(err)

        print('Claim your port to listen: ', ports)
        my_port = eval(input('Your choice: '))
        try:
            listener_socket.bind((host, my_port))
            print('Set up listener successfully!')
            break
        except OSError:
            print('/!\ Address already in use. Please try again!')

    t_listener = threading.Thread(target=listener_thread)
    t_listener.start()
    threads.append(t_listener)

    # Set up connection
    for i in range(number_of_peers):
        # Set up request thread
        print('Connect to machine ', i)
        while True:
            # target_host = host
            target_host = input('Input target IP Address (e.g. 192.168.1.111): ')
            target_port = eval(input('Input target Port number (e.g. 7777): '))
            # assume inputs are valid
            try:
                socket.inet_aton(target_host)
                request_socket.connect((target_host, target_port))
                message = request_socket.recv(1024)  # thank you for connecting
                print(message.decode('utf-8'))
                break
            except socket.error as err:
                print(err)
                continue
            except ConnectionRefusedError:
                print('/!\ Port is not ready to use. Please try another')
                continue
        t_request = threading.Thread(target=request_thread)
        t_request.start()
        threads.append(t_request)
        print('> Connection established!')

path_windows = home_dir + '/test_windows/'


def simulator():
    global path
    is_windows = eval(input('Are you Windows (1 | 0): '))
    if is_windows == 1:
        path = path_windows


# simulator()  # comment this function when delivery

load_files()
get_user_input()

for t in threads:
    t.join()
