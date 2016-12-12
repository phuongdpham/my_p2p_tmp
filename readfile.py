import os
import pickle
import time
import glob

homedir = os.path.expanduser('~')
path = homedir + '/test/'

# files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]  # and not f.startswith('.')]

# os.utime(file, (1481481815.7199235, 1481481815.7199235))

if not os.path.exists(path):
    print('create')
    os.makedirs(path)
else:
    print('exists')

file = 'build.txt'

os.chdir(path)

with open(file, 'wb') as txt:
    txt.write(pickle.dumps('abc'))
lm = os.path.getatime(file)
os.utime(file, (lm, round(lm)))

print(os.path.getmtime(file))

with open(file, 'rb') as reader:
    print(pickle.loads(reader.read()))

# Showing stat information of file

