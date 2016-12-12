import queue
import threading
from _thread import *
import asyncio

number = 0
lock = threading.RLock()


def do_work(item, i):
    global number
    # print(item, i)
    #     for it in range(5):
    #         print(item, it)
    lock.acquire()
    try:
        while number < 10:
            number += 1
            print(number)
    finally:
        lock.release()


threads = []
num_of_threads = 3

for i in range(num_of_threads):
    t = threading.Thread(target=do_work, args=(i, i))
    t.start()
    t.join()
    # threads.append(t)
    # start_new_thread(do_work, (i, i))

# for t in threads:
#     t.join()
