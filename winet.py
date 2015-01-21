#!/usr/bin/env python
# coding=utf-8

# WiNet.py
# Complemento ao WiSync.py
# Copyright (C) 2015 Renan Greca <rdmg11@inf.ufpr.com>

# Usado para lidar com o diretório remoto
# Parte do conteúdo é baseado em woof.py <http://www.home.unix-ag.org/simon/woof.html>

import socket
import sys
import urllib2

from os.path import join

from time import sleep

from woof import serve_files

class Net():
    def __init__(self, hostname=None):
        self.host = socket.gethostname()
        if self.host.endswith('.local'):
            self.ip = socket.gethostbyname(self.host)
        else:
            self.ip = socket.gethostbyname(self.host+'.local')

        self.remote_addr = None
        if hostname is not None:
            if hostname.endswith('.local'):
                self.remote_addr = socket.gethostbyname(hostname)
            else:
                self.remote_addr = socket.gethostbyname(hostname+'.local')

    def client(self, direc, again=False):
        filename = 'files.json'
        data = None
        if self.remote_addr is not None:
            try:
                response = urllib2.urlopen('http://'+self.remote_addr+':8080/'+filename, timeout=0.1);
                data = chunk_read(response, filename, report_hook=chunk_report)
            except Exception:
                print "Servidor não encontrado"
                pass
        else:
            data = self.findserver(filename)
        if data is None:
            if not again:
                self.serve(direc)
                sleep(1)
                self.client(direc, again=True)
        else:
            f = open(join(direc.auxdir, 'rfiles.json'), "w")
            f.write(data)
            f.close()
            if not again:
                self.serve(direc)
            # Fazer resto da parte cliente

    def findserver(self, filename):
        ips = self.ip.split('.')
        for i in range(2, 254):
            host = ips[0]+'.'+ips[1]+'.'+ips[2]+'.'+str(i)

            addr = 'http://%s:8080/%s' % (host, filename)
            sys.stdout.write("\rBuscando arquivo... %s" % addr)
            sys.stdout.flush()
            try:
                response = urllib2.urlopen(addr, timeout=0.01);
                sys.stdout.write("\n")
                return chunk_read(response, filename, report_hook=chunk_report)
            except Exception:
                pass
        print "Servidor não encontrado"
        return None

    def serve(self, direc):
        filename = join(direc.auxdir, 'files.json')
        print "Hospedando arquivo", filename
        serve_files(filename, maxdown=1, ip_addr='', port=8080)


# funções auxiliares
def chunk_report(bytes_so_far, chunk_size, total_size, filename):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write("Baixando arquivo %s (%0.2f%%)\r" % (filename, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def chunk_read(response, filename, chunk_size=8192, report_hook=None):
    total_size = response.info().getheader('Content-Length').strip()
    total_size = int(total_size)
    bytes_so_far = 0

    data = None

    while 1:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)

        if not chunk:
            break

        if data is None:
            data = chunk
        else:
            data += chunk

        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size, filename)

    return data

# serve_files ('a.jpg', maxdown=1, ip_addr='', port=8080)