# Simple Server from example 2.1

from socket import *

s = socket(AF_INET, SOCK_STREAM)
(conn, addr) = s.accept()
while True:
    data = conn.recv(1024)
    if not data:
        break
    conn.send(str(data) + "*")
conn.close()
