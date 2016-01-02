#!/usr/bin/env python
# coding=utf-8

# WiFiles.py
# Complemento ao WiSync.py
# Copyright (C) 2015 Renan Greca <rdmg11@inf.ufpr.com>

# Usado para lidar com o diretório local

import socket
from pickle import load
import json
from os import listdir, makedirs
from os.path import isfile, isdir, join, getmtime, getctime, exists
from datetime import datetime


class WiFiles():
    def __init__(self, direc):
        """ Classe usada para gerenciar a parte de arquivos do WiSync.

        :: PARAMS ::
        :str direc:
            Caminho para o diretório a ser usado.
        """
        self.dir = direc
        if not exists(self.dir):
            exit("Diretório não existente.")

        if not isdir(self.dir):
            exit("Caminho deve ser um diretório.")

        self.auxdir = join(self.dir, '.wisync')
        if not exists(self.auxdir):
            print "Novo diretório encontrado, criando arquivos auxiliares..."
            makedirs(self.auxdir)
        
        #if exists(join(self.auxdir, '.last_sync.pkl')):
        #    # Obtém as informações da última sincronização
        #    self.last_sync = load(join(self.auxdir, '.last_sync.pkl'))

        self.files = self.read_dir()
        data = json.dumps(self.files.dict())
        # Saves current status of files into files.json
        f = open(join(self.auxdir, 'files.json'), 'w')
        f.write(data)
        f.close()

        self.hostname = socket.gethostname()
        self.remote_hostname = None

    def read_dir(self, direc=None, level=0):
        """ Lê um diretório e armazena informações sobre os arquivos contidos nele.

        :: PARAMS ::
        :str direc:
            Diretório a ser lido.
            Se for None, o diretório da classe é usado.
            (padrão: None)

        :int level:
            Nível da recursão para subdiretórios.
            (padrão: 0)

        :: RETURNS ::
        Dicionário contendo:
            Todos os arquivos do diretório e dos subdiretórios.
        """

        if direc is None:
            direc = self.dir

        dirs = direc.split('/')
        dirname = dirs.pop()
        # files = {}

        datem, datec = dates(direc)
        files = File(dirname, datem, datec, isDir=True)

        for f in listdir(direc):
            datem, datec = dates(join(direc, f))
            if isfile(join(direc, f)):
                # Pega as datas de modificação e criação do arquivo
                files.add_file(File(f, datem, datec))
                # files[f] = {'type': 'f', 'datem': datem, 'datec': datec}
            else:
                if (join(direc, f)) == self.auxdir:
                    # Pula diretório de dados do WiSync
                    continue
                # Pega os arquivos de dentro de um diretório recursivamente
                files.add_file(self.read_dir(join(direc, f), level+1))
                # files[f] = {'type': 'd', 'datem': datem, 'datec': datec,
                #               'conteudo': self.read_dir(join(direc,f), level+1)}

        return files

    # Compara o diretório atual com o armazenado no pkl
    # e toma as decisões adequadas.
    def compare_dirs(self):
        # Dir A é o JSON contendo informações do diretório local
        try:
            print join(self.auxdir, 'files.json')
            with open(join(self.auxdir, 'files.json'), 'r') as json_file:
                dir_a = json.load(json_file)
        except Exception:
            print "[F] files.json não encontrado!"
            return

        # Dir B é o JSON contendo informações do diretório remoto
        try:
            with open(join(self.auxdir, 'rfiles.json'), 'r') as json_file:
                dir_b = json.load(json_file)
        except Exception:
            print "[F] rfiles.json não encontrado!"
            return

        # Dir C é o JSON contendo informações do estado do diretório após a última sincronização
        try:
            with open(join(self.auxdir, 'last_sync.json'), 'r') as json_file:
                dir_c = json.load(json_file)

            if dir_a['datem'] == dir_c['datem']:
                print 'Diretório A não mudou'

            if dir_b['datem'] == dir_c['datem']:
                print 'Diretório B não mudou'

            changes_a = compare_with_previous(dir_a['files'], dir_c['files'])
            changes_a['deleted'] = check_deleted(dir_a['files'], dir_b['files'], dir_c['files'])

            changes_b = compare_with_previous(dir_b['files'], dir_c['files'])
            changes_b['deleted'] = check_deleted(dir_b['files'], dir_a['files'], dir_c['files'])

        except Exception:
            print "[F] last_sync.json não encontrado!"
            print "[F] Realizando sincronização inicial."

            if dir_a['datem'] == dir_b['datem']:
                print 'Diretórios não mudaram'

            changes_a = compare_with_previous(dir_a['files'], dir_b['files'])

            changes_b = compare_with_previous(dir_b['files'], dir_a['files'])

        resolve_conflicts(changes_a["created"], changes_b["created"], self.hostname)
        resolve_conflicts(changes_b["created"], changes_a["created"], self.remote_hostname)

        resolve_conflicts(changes_a["altered"], changes_b["altered"], self.hostname)
        resolve_conflicts(changes_b["altered"], changes_a["altered"], self.remote_hostname)

        changes = {'server': changes_a, 'client': changes_b}

        data = json.dumps(changes)
        # Saves current status of files into files.json
        with open(join(self.auxdir, 'changes.json'), 'w') as f:
            f.write(data)

        return changes
        #return changes_a, changes_b

    def save(self):
        """
        Salva a situação atual do diretório num arquivo para referência futura.
        Normalmente será a última coisa a ser chamada no programa.
        """
        files = self.read_dir()
        data = json.dumps(files.dict())
        f = open(join(self.auxdir, 'last_sync.json'), 'w')
        f.write(data)
        f.close()


def resolve_conflicts(a, b, hostname):
    for name, f in a.iteritems():
        if f['isDir']:
            if name in b and b[name]['isDir']:
                resolve_conflicts(f['files'], b[name]['files'], hostname)
        else:
            if name in b:
                if f['datem'] != b[name]['datem'] and not f['isDir']:
                    newname = '(' + hostname + ') ' + name
                    a[name]['name'] = newname

def compare_with_previous(files, oldfiles, check_removed=True):
    changes = {
        "created": {},
        "altered": {},
        "deleted": {}
    }

    print 'Procurando arquivos novos ou modificados'
    changes["created"], changes["altered"] = compare(files, oldfiles)

    # if check_removed:
    #     print 'Procurando arquivos removidos'
    #     changes["deleted"], ignore = compare(oldfiles, files)

    return changes


def compare(a, b):
    created = {}
    altered = {}

    for name, file in a.iteritems():
        if name == '.DS_Store' or name == 'desktop.ini':
            continue

        if file['isDir']:
            if name in b and b[name]['isDir']:
                c, a = compare(file['files'], b[name]['files'])
                if len(c) > 0:
                    created[name] = file
                    created[name]['files'] = c
                if len(a) > 0:
                    altered[name] = file
                    altered[name]['files'] = a
            else:
                created[name] = file
        else:
            if name in b:
                if file['datem'] > b[name]['datem']:
                    #print 'Arquivo ', name, ' foi modificado'
                    altered[name] = file
            else:
                created[name] = file

    return created, altered


def check_deleted(a, b, c):
    deleted = {}

    for name, f in c.iteritems():
        if name == '.DS_Store' or name == 'desktop.ini':
            continue

        if f['isDir']:
            if name in a and name in b:
                d = check_deleted(f['files'], a[name]['files'], b[name]['files'])
                deleted[name] = f
                deleted[name]['files'] = d
        else:
            if name not in a:
                # from IPython import embed
                # embed()
                if f['datem'] == b[name]['datem']:
                    # Arquivo foi excluído em A e não modificado em B
                    print 'Arquivo ', name, ' foi excluído em A'
                    deleted[name] = f
            # if name not in b:
            #     if f['datem'] <= a[name]['datem']:
            #         # Arquivo foi excluído em B e não modificado em A
            #         print 'Arquivo ', name, ' foi excluído em B'
            #         deleted[name] = f

    return deleted


class File():

    def __init__(self, name, datem, datec, isDir=False):
        self.name = name
        self.datem = datem
        self.datec = datec
        self.isDir = isDir
        if self.isDir:
            self.files = {}

    def add_file(self, f):
        if not self.isDir:
            print "Objeto não é um diretório"
            return
        self.files[f.name] = f

    def dict(self):
        d = self.__dict__
        if self.isDir:
            files = {}
            for name, f in self.files.iteritems():
                files[name] = f.dict()
            d['files'] = files
        return d

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
    datem = datetime.fromtimestamp(getmtime(f)).isoformat().split('.')[0]
    datec = datetime.fromtimestamp(getctime(f)).isoformat().split('.')[0]
    return datem, datec


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