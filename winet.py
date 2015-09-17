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
import errno
import traceback

from wifiles import WiFiles

from os.path import join

from time import sleep

from woof import serve_files

class WiNet():
    def __init__(self, direc, hostname, isServer):
        """ Classe usada para gerenciar a parte em rede do WiSync.

        :: PARAMS ::
        :str hostname:
            Nome de rede de um computador rodando outra instância do WiSync.
            (padrão: None)
        """
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

        self.isServer = isServer
        self.username = "WiSync"
        self.password = "WiSync"
        self.direc = direc

    def server(self):
        filename = join(self.direc.auxdir, 'files.json')
        print "[S] Hospedando arquivo", filename, "\n"
        self.remote_addr = serve_files(filename, maxdown=1, ip_addr='', port=8080)
        print "[S] Terminou de hospedar arquivo"

        sleep(1)
        self.client()

    def client(self):
        """ Parte de cliente do programa.
            Usado quando o programa estiver recebendo arquivos da outra instância.

        :: PARAMS ::
        :str direc:
            Diretório sendo usado pelo WiSync.

        :bool again:
            Usado para evitar recursões.
            (padrão: False)
        """
        filename = 'files.json'
        data = self.remote_file(filename)

        #if not self.isServer:
        #    self.isServer = True
        #    self.serve(direc)
        print data
        if data is not None:
            f = open(join(self.direc.auxdir, 'rfiles.json'), "w")
            f.write(data)
            f.close()
            if not self.isServer:
                self.serve(self.direc)
            else:
                self.compare_dirs()
            # TODO Fazer resto da parte cliente

    def remote_file(self, filename):
        if self.remote_addr is not None:
            try:
                response = urllib2.urlopen('http://'+self.remote_addr+':8080/'+filename, timeout=1)
                return chunk_read(response, filename, report_hook=chunk_report)
            except urllib2.HTTPError, e:
                print '[C] HTTPError = ' + str(e.code)
            except urllib2.URLError, e:
                #print 'URLError = ' + str(e.reason)
                print "\n[C] Servidor não encontrado"
                pass
            except Exception as e:
                if e.errno == 104:
                    pass
                else:
                    print '[C] Erro: ' + traceback.format_exc()

        else:
            ips = self.ip.split('.')
            for i in range(2, 254):
                host = ips[0]+'.'+ips[1]+'.'+ips[2]+'.'+str(i)

                if host == self.ip:
                    continue
                addr = 'http://%s:8080/%s' % (host, filename)
                sys.stdout.write("\r[C] Buscando arquivo... %s" % addr)
                sys.stdout.flush()
                try:
                    response = urllib2.urlopen(addr, timeout=0.1)
                    sys.stdout.write("\n")
                    self.remote_addr = addr
                    return chunk_read(response, filename, report_hook=chunk_report)
                except Exception:
                    pass

            #return self.findserver(filename)

    def findserver(self, filename='files.json'):
        """ Usado para encontrar uma outra instância do programa na rede local.

        :: PARAMS ::
        :str filename:
            Nome do arquivo a ser encontrado no outro servidor.
            (padrão: 'files.json')

        :: RETURNS ::
        Uma variável contendo:
            None, se der algo errado.
        """
            #print "[C] Servidor não encontrado115"
            #return None

    def serve(self, direc):
        filename = join(direc.auxdir, 'files.json')
        print "Hospedando arquivo", filename, "\n"
        serve_files(filename, maxdown=1, ip_addr='', port=8080)
        #if self.isServer:
        #    sleep(1)
        #    self.client(direc)

    def compare_dirs(self):
        direc = WiFiles(self.direc)
        direc.compare_dirs()

# funções auxiliares
def chunk_report(bytes_so_far, chunk_size, total_size, filename):
    """ Mostra o progresso durante o download de um arquivo.

    :: PARAMS ::
    :int bytes_so_far:
        Quantidade de bytes já baixados.

    :int chunk_size:
        Tamanho de cada bloco em bytes.

    :int total_size:
        Tamanho total do arquivo em bytes.

    :str filename:
        Nome do arquivo.
    """
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write("Baixando arquivo %s (%0.2f%%)\r" % (filename, percent))

    if bytes_so_far >= total_size:
        sys.stdout.write('\n')


def chunk_read(response, filename, chunk_size=8192, report_hook=None):
    """ Baixa um arquivo em blocos para poder exibir o progresso.

    :: PARAMS ::
    :http response:
        Resposta HTTP resultante de um urllib2.urlopen().

    :str filename:
        Nome do arquivo.

    :int chunk_size:
        Tamanho de cada bloco em bytes.

    :func report_hook:
        Função a ser chamada após cada bloco ser lido.
        (padrão: None)

    :: RETURNS ::
    Uma variável contendo:
        Os dados do arquivo recebido.
    """
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