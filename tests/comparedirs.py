#!/usr/bin/env python
# coding=utf-8
__author__ = 'renangreca'

import os
from os.path import join
import json
import datetime

directory = os.path.dirname(os.path.realpath(__file__))

def compare_dirs(dir, level=0):
    modified = {}
    added = {}

    countries = json.load(open(os.path.join(dir, 'files.json'), 'r'))

    # Dir A é o JSON contendo informações do diretório local
    try:
        with open(join(dir, 'files.json'), 'r') as json_file:
            dir_a = json.load(json_file)
    except Exception:
        print "[F] files.json não encontrado!"
        return

    # Dir B é o JSON contendo informações do diretório remoto
    try:
        dir_b = json.load(open(join(dir, 'rfiles.json'), 'r'))
    except Exception:
        print "[F] rfiles.json não encontrado!"
        return

    # Dir C é o JSON contendo informações do estado do diretório após a última sincronização
    try:
        dir_c = json.load(open(join(dir, 'last_sync.json'), 'r'))
    except Exception:
        print "[F] last_sync.json não encontrado!"
        return

    if dir_a['datem'] == dir_c['datem']:
        print 'Diretório não mudou'

    (a_to_b, b_to_a) = compare_a_and_b(dir_a['files'], dir_b['files'])

    print a_to_b
    print b_to_a

    #return modified, added

def compare_a_and_b(files, rfiles):
    # Compare Dir A with Dir B
    a_to_b = []
    b_to_a = []

    print 'Checking for new files in A'
    for name, file in files.iteritems():
        if file['isDir']:

        else:
            if name in rfiles:
                print 'In common: ', name
                if file['datem'] > rfiles[name]['datem']:
                    print 'File ', name, ' has been changed'
                    a_to_b.append(name)
            else:
                print 'Different: ', name
                a_to_b.append(name)

    print 'Checking for new files in B'
    for name, file in rfiles.iteritems():
        if name in files:
            print 'In common: ', name
            if file['datem'] > files[name]['datem']:
                print 'File ', name, ' has been changed'
                b_to_a.append(name)
        else:
            print 'Different: ', name
            b_to_a.append(name)

    return a_to_b, b_to_a

class File:

    def __init__(self, name, datem, datec, is_dir=False):
        self.name = name
        self.datem = datem
        self.datec = datec
        self.is_dir = is_dir
        if self.is_dir:
            self.files = []

    def add_file(self, f):
        if not self.is_dir:
            print "Objeto não é um diretório"
            return
        self.files.append(f)

    def dict(self):
        d = self.__dict__
        if self.is_dir:
            files = []
            for f in self.files:
                files.append(f.dict())
            d['files'] = files
        return d


# Lê informações do diretório
def read_dir(direc, nivel=0):
    arquivos = {}

    for f in listdir(direc):
        datam, datac = dates(join(direc, f))
        if isfile(join(direc, f)):
            # Pega as datas de modificação e criação do arquivo
            arquivos[f] = {"tipo": 'f', 'datam': datam, 'datac': datac}
        else:
            # Pega os arquivos de dentro de um diretório recursivamente
            arquivos[f] = {'tipo': 'd', 'datam': datam, 'datac': datac,
                           'conteudo': read_dir(join(direc,f), nivel+1)}

    return arquivos

# Operações auxiliares
def dates(f):
    """ Pega as datas e horas de criação e modificação de um arquivo.
        As datas são retornadas em formato ISO.
        Ex: 2015-01-21T19:08:34.987381

    :: PARAMS ::
    :file f:
        Arquivo cujas datas serão lidas.

    :: RETURNS ::
    Tupla contendo:
        Data de modificação do arquivo.
        Data de criação do arquivo.
    """
    datem = datetime.fromtimestamp(getmtime(f)).isoformat()
    datec = datetime.fromtimestamp(getctime(f)).isoformat()
    return datem, datec

if __name__ == '__main__':
    compare_dirs(directory, level=0)
