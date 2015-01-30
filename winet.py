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

        self.isServer = False

    def client(self, direc, again=False):
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
        data = None

        print "Endereço remoto:",self.remote_addr
        if self.remote_addr is not None:
            try:
                response = urllib2.urlopen('http://'+self.remote_addr+':8080/'+filename, timeout=0.5);
                data = chunk_read(response, filename, report_hook=chunk_report)
            except Exception:
                print "Servidor não encontrado"
                pass
        else:
            data = self.findserver(filename)
        if data is None:
            if not again:
                self.isServer = True
                self.serve(direc)
                sleep(2)
                print "Hi!", self.isServer, again
                self.client(direc, again=True)
        else:
            print "Arquivo recebido. Salvando em rfiles.json"
            print self.isServer
            f = open(join(direc.auxdir, 'rfiles.json'), "w")
            f.write(data)
            f.close()
            if not again:
                self.serve(direc)
            # TODO Fazer resto da parte cliente

    def findserver(self, filename='files.json'):
        """ Usado para encontrar uma outra instância do programa na rede local.

        :: PARAMS ::
        :str filename:
            Nome do arquivo a ser encontrado no outro servidor.
            (padrão: 'files.json')

        :: RETURNS ::
        Uma variável contendo:
            O conteúdo do arquivo, se a função for bem-sucedida.
            None, se der algo errado.
        """
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