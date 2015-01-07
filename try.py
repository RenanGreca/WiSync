#!/usr/bin/env python
# coding=utf-8

import argparse
import socket
import sys
import threading
from time import sleep
from multiprocessing import Process
from socklib import Server
from socklib import Client

parser = argparse.ArgumentParser(description='Sends some data back and forth.')
parser.add_argument('-n', '--hostname', type=str, required=True,
                   help='Nome de rede do outro computador')
parser.add_argument('-s', '--server', default=False, const=True, action='store_const',
                   help='Forçar modo servidor')

args = parser.parse_args()

def findserver():
    host = socket.gethostname()
    if host.endswith('.local'):
        ip = socket.gethostbyname(host)
    else:
        ip = socket.gethostbyname(host+'.local')

    ips = ip.split('.')
    for i in range(2, 254):
        #sleep(0.01)
        host = ips[0]+'.'+ips[1]+'.'+ips[2]+'.'+str(i)
        #print 'Buscando servidor ... [%d/254]\r'%i,

        sys.stdout.write('Buscando servidor ... [%d/254]\r'%i)
        sys.stdout.flush()

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print 'Conectando ao servidor: '+host+':'+str(port)
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

            proc.join()
            s.close()
            return True
        except Exception, e:
            #print 'fail', e
            pass
        

    return False

def client():

    if not args.hostname:
        return findserver()

    hostname = args.hostname

    if hostname.endswith('.local'):
        host = socket.gethostbyname(hostname)
    else:
        host = socket.gethostbyname(hostname+'.local')
    port = 50000
    size = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #print 'Conectando ao servidor: '+host+':'+str(port)
    s.connect((host,port))
    sys.stdout.write('%')

    while 1:
        # read from keyboard
        line = sys.stdin.readline()
        if line == '\n':
            break
        s.send(line)
        data = s.recv(size)
        #sys.stdout.write(data)
        sys.stdout.write('%')

    proc.join()
    s.close()

    return True

if __name__ == '__main__':
    
    if args.server:
        server = Server()
        server.run()

    else:
        if not client():
            print "Não há servidor rodando! Iniciando em modo servidor..."

            server = Server()
            server.run()