import os
import time
import glob

homedir = os.path.expanduser('~')
path = homedir + '/test/'
file = 'build.txt'

# files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]  # and not f.startswith('.')]

# os.utime(file, (1481481815.7199235, 1481481815.7199235))

if not os.path.exists(path):
    print('create')
    os.makedirs(path)
else:
    print('exists')

os.chdir(path)

# Showing stat information of file
stat_info = os.stat(file)
print(stat_info.st_mtime_ns)

with open(file, errors='ignore') as txt:
    data = txt.read()
    print(data)

os.utime(file, (stat_info.st_atime_ns, stat_info.st_mtime_ns))
