# Simple client from Note 2.1
#
from socket import *
s = socket(AF_INET, SOCK_STREAM)
s.connect(HOST, PORT)
s.send('Hello, world')
data = s.recv(1024)
print data
s.close()
