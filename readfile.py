import os
import pickle
import time
import glob

homedir = os.path.expanduser('~')
path = homedir + '/test/'

files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]  # and not f.startswith('.')]

# os.utime(file, (1481481815.7199235, 1481481815.7199235))

if not os.path.exists(path):
    print('create')
    os.makedirs(path)
else:
    print('exists')

file = 'build.txt'

os.chdir(path)

data = pickle.dumps(files, protocol=3)
d = pickle.loads(data)

print(files.__sizeof__())
# print(d)

print(files is d, files == d)

