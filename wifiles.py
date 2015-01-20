#!/usr/bin/env python
# coding=utf-8
# UTF-8 para poder usar acentos

import socket
import argparse
from pickle import load, dump
from json import loads, dumps
from os import listdir
from os.path import isfile, join, getmtime, getctime, exists
from time import ctime
from datetime import datetime

class Dir():
    def __init__(self, dir):
        self.dir = dir
        if not exists(self.dir):
            exit("Diretório não existente.")

        if isfile(self.dir):
            exit("Caminho deve ser um diretório, não um arquivo.")

        self.auxdir = join(self.dir, '.wisync')
        if not exists(self.auxdir):
            print "Novo diretório encontrado, criando arquivos auxiliares..."
            makedirs(self.auxdir)
        
        if exists(join(self.auxdir, '.last_sync.pkl')):
            # Obtém as informações da última sincronização
            self.last_sync = load(join(self.auxdir, '.last_sync.pkl'))

        self.files = self.read_dir()
        self.remote_files = None

    def read_dir(self, dir=None, level=0):
        if dir is None:
            dir = self.dir
        files = {}

        for f in listdir(dir):
            datem, datec = dates(join(dir, f))
            if isfile(join(dir, f)):
                # Pega as datas de modificação e criação do arquivo
                files[f] = {'type': 'f', 'datem': datem, 'datec': datec}
            else:
                # Pega os arquivos de dentro de um diretório recursivamente
                files[f] = {'type': 'd', 'datem': datem, 'datec': datec,
                               'conteudo': self.read_dir(join(dir,f), level+1)}

        return files

    def save(self):
        files = self.read_dir()
        data = dumps(files)
        f = open(join(self.auxdir, 'last_sync.json'), 'w')
        f.write(data)
        f.close


# Operações auxiliares
def dates(f):
    datam = datetime.fromtimestamp(getmtime(f)).isoformat()
    datac = datetime.fromtimestamp(getctime(f)).isoformat()
    return datam, datac

# Lê informações do diretório
def ler_dir(dir, nivel=0):
    arquivos = {}

    for f in listdir(dir):
        datam, datac = datas(join(dir, f))
        if isfile(join(dir, f)):
            # Pega as datas de modificação e criação do arquivo
            arquivos[f] = {"tipo": 'f', 'datam': datam, 'datac': datac}
        else:
            # Pega os arquivos de dentro de um diretório recursivamente
            arquivos[f] = {'tipo': 'd', 'datam': datam, 'datac': datac,
                           'conteudo': ler_dir(join(dir,f), nivel+1)}

    return arquivos

# Compara o diretório atual com o armazenado no pkl
# e toma as decisões adequadas.
def compara_dirs(dir, dir_atual, dir_anterior):
    modificados = {}
    adicionados = {}

    for nome, arquivo in dir_atual.iteritems():
        if isfile(join(dir, nome)):
            if (nome in dir_anterior):
                if (dir_atual[nome]['datam'] != dir_anterior[nome]['datam']):
                    modificados[nome] = dir_atual[nome]
            else:
                adicionados[nome] = dir_atual[nome]
        else:
            modificados[nome], adicionados[nome] = compara_dirs(join(dir, nome), arquivo['conteudo'], dir_anterior)

    return modificados, adicionados

def main(args):

    dir_atual = ler_dir(args.directory)

    if (exists(join(args.directory, '.sync.pkl'))):
        dir_anterior = pickle.load(open(join(args.directory, '.sync.pkl')))

    pickle.dump(dir_atual, open(join(args.directory, '.sync.pkl'), 'w'))

    mudancas = compara_dirs(args.directory, dir_atual, dir_anterior)

    print 'Dir atual: ',dir_atual
    print 'Dir anterior',dir_anterior
    print 'Mudanças: ',mudancas

    return;
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

    print SERVER_IP, CLIENT_IP

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