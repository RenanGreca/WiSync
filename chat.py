#!/usr/bin/env python

import socket
import argparse

parser = argparse.ArgumentParser(description='Sends some data back and forth.')
parser.add_argument('-n', '--hostname', type=str,
                   help='Network name of the other computer')

args = parser.parse_args()

# Gets the remote IP address
hostname = args.hostname
if hostname.endswith('.local'):
    CLIENT_IP = socket.gethostbyname(hostname)
else:
    CLIENT_IP = socket.gethostbyname(hostname+'.local')

# Gets the current computer's IP address
hostname = socket.gethostname()
if hostname.endswith('.local'):
    SERVER_IP = socket.gethostbyname(hostname)
else:
    SERVER_IP = socket.gethostbyname(hostname+'.local')

TCP_PORT = 5005
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((SERVER_IP, TCP_PORT))
s.listen(1)
print 'Server is running with IP', SERVER_IP

c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Trying to connect with client', CLIENT_IP
c.connect((CLIENT_IP, TCP_PORT))

conn, addr = s.accept()
print 'Connection address:', addr
while 1:
    message = raw_input('Here: ')
    c.send(message)
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print "There: ", data
    conn.send(data)  # echo
conn.close()

data = c.recv(BUFFER_SIZE)
c.close()