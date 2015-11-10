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
import json

from wifiles import WiFiles

from os import makedirs, remove
from os.path import join, exists

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
        print hostname
        if hostname is not None:
                try:
                    if hostname.endswith('.local'):
                        self.remote_addr = socket.gethostbyname(hostname)
                    else:
                        self.remote_addr = socket.gethostbyname(hostname+'.local')
                except Exception:
                    self.remote_addr = hostname

        self.isServer = isServer
        self.username = "WiSync"
        self.password = "WiSync"
        self.direc = direc
        self.changes = {}

    def server(self):
        filename = join(self.direc.auxdir, 'files.json')
        print "[S] Hospedando arquivo", filename, "\n"
        self.remote_addr = serve_files(filename, maxdown=1, ip_addr='', port=8080)
        print "[S] Terminou de hospedar arquivo"

        sleep(1)
        filename = 'files.json'
        data = self.remote_file(filename)
        if data is not None:
            with open(join(self.direc.auxdir, 'rfiles.json'), "w") as f:
                f.write(data)
            changes = self.compare_dirs()

            print 'Preparando para enviar arquivos...'
            self.send_files(changes['server']['created'])

            print 'Envio de arquivos concluído. Preparando para receber...'
            sleep(4)
            self.receive_files(changes['client']['created'])

            print 'Troca de arquivos concluída. Realizando passos finais...'
            self.clean_up(changes['client']['deleted'])

        #self.client()

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
        if data is not None:
            with open(join(self.direc.auxdir, 'rfiles.json'), "w") as f:
                f.write(data)
            filename = join(self.direc.auxdir, 'files.json')
            self.serve(filename)

            sleep(1)
            self.changes = self.remote_file('changes.json')
            with open(join(self.direc.auxdir, 'changes.json'), "w") as f:
                f.write(self.changes)

            with open(join(self.direc.auxdir, 'changes.json'), "r") as f:
                changes = json.load(f)

            print 'Preparando para receber arquivos...'
            sleep(1)
            self.receive_files(changes['server']['created'])

            print 'Recebimento de arquivos concluído. Preparando para enviar...'
            self.send_files(changes['client']['created'])

            print 'Troca de arquivos concluída. Realizando passos finais...'
            self.clean_up(changes['server']['deleted'])

    def remote_file(self, filename):

        if self.remote_addr is not None:
            try:
                print 'http://'+self.remote_addr+':8080/'+filename
                response = urllib2.urlopen('http://'+self.remote_addr+':8080/'+filename, timeout=100)
                return chunk_read(response, filename, report_hook=chunk_report)
            except urllib2.HTTPError, e:
                print '[C] HTTPError = ' + str(e.code)
                exit()
            except urllib2.URLError, e:
                #print 'URLError = ' + str(e.reason)
                print "\n[C] Servidor não encontrado"
                exit()
            except Exception as e:
                print '[C] Erro: ' + traceback.format_exc()
                exit()

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

    def serve(self, filename):
        print "Hospedando arquivo", filename, "\n"
        remote_addr = serve_files(filename, maxdown=1, ip_addr='', port=8080)
        print remote_addr, filename

    def compare_dirs(self):
        #direc = WiFiles(self.direc)
        changes = self.direc.compare_dirs()
        filename = join(self.direc.auxdir, 'changes.json')
        self.serve(filename)

        return changes

    def send_files(self, files, directory=None):
        if directory is None:
            directory = self.direc.dir

        import operator
        filelist = sorted(files.items(), key=operator.itemgetter(0))
        for name, f in filelist:
            # Ignora arquivos de sistema (do OS X e do Windows)
            if name == '.DS_Store' or name == 'desktop.ini':
                continue

            if f['isDir']:
                self.send_files(f['files'], directory=join(directory, f['name']))
            else:
                filename = join(directory, name)
                self.serve(filename)

    def receive_files(self, files, directory=None):
        if directory is None:
            directory = self.direc.dir

        import operator
        filelist = sorted(files.items(), key=operator.itemgetter(0))
        for name, f in filelist:
            # Ignora arquivos de sistema (do OS X e do Windows)
            if name == '.DS_Store' or name == 'desktop.ini':
                continue

            if f['isDir']:
                dirs = name.split('/')
                dirname = join(directory, dirs.pop())
                if not exists(dirname):
                    makedirs(dirname)
                self.receive_files(f['files'], dirname)
            else:
                sleep(1)
                data = self.remote_file(urllib2.quote(name))
                with open(join(directory, name), "w") as d:
                    d.write(data)

    def clean_up(self, files, directory=None):
        if directory is None:
            directory = self.direc.dir

        import operator
        filelist = sorted(files.items(), key=operator.itemgetter(0))
        for name, f in filelist:
            # Ignora arquivos de sistema (do OS X e do Windows)
            if name == '.DS_Store' or name == 'desktop.ini':
                continue

            if f['isDir']:
                self.clean_up(f['files'], directory=join(directory, f['name']))
            else:
                filename = join(directory, name)
                remove(filename)

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