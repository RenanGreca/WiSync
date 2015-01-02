#!/usr/bin/env python
# coding=utf-8

import argparse
import socket
import sys
import threading
from socklib import Server
from socklib import Client

#parser = argparse.ArgumentParser(description='Sends some data back and forth.')
#parser.add_argument('-n', '--hostname', type=str, required=True,
#                   help='Network name of the other computer')

#args = parser.parse_args()


"""
An echo client that allows the user to send multiple lines to the server.
Entering a blank line will exit the client.
"""

server = Server()
server.run()

host = 'localhost'
port = 50000
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
sys.stdout.write('%')

while 1:
    # read from keyboard
    line = sys.stdin.readline()
    if line == '\n':
        break
    s.send(line)
    data = s.recv(size)
    sys.stdout.write(data)
    sys.stdout.write('%')
s.close()