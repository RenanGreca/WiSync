#!/usr/bin/env python
# coding=utf-8

"""
An echo server that uses threads to handle multiple clients at a time.
Entering any line of input at the terminal will exit the server.
"""

import select
import socket
import sys
import threading

class Server():
    def __init__(self):
        # Utilizando o nome do host (o computador rodando o script)
        # Encontramos seu endereço IP local
        self.host = socket.gethostname()
        if self.host.endswith('.local'):
            self.ip = socket.gethostbyname(self.host)
        else:
            self.ip = socket.gethostbyname(self.host+'.local')
        #self.host = ''
        self.port = 50000
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.ip,self.port))
            self.server.listen(5)

            print "Servidor rodando - "+self.ip+':'+str(self.port)
            print self.server
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        self.open_socket()
        input = [self.server,sys.stdin]
        running = 1
        while running:
            inputready,outputready,exceptready = select.select(input,[],[])

            for s in inputready:

                if s == self.server:
                    # handle the server socket
                    c = Client(self.server.accept())
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    line = sys.stdin.readline()
                    if line == '\n':
                        break
                        running = 0 
                    for client in self.threads:
                        client.client.send(line)

        # close all threads

        self.server.close()
        for c in self.threads:
            c.join()

class Client(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024

    def run(self):
        running = 1
        while running:
            data = self.client.recv(self.size)
            if data:
                if data == 'file\n':
                    print "Recebendo arquivo..."
                    stuff = self.client.recv(self.size)
                    f = open("out", "w")
                    f.write(stuff)
                    f.close()
                else:
                    sys.stdout.write(">")
                    sys.stdout.write(data)
                    #self.client.send(data)
            else:
                self.client.close()
                running = 0