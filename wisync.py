#!/usr/bin/env python
# coding=utf-8

# WiSync.py
# Copyright (C) 2015 Renan Greca <rdmg11@inf.ufpr.com>

# Bibliotecas auxiliares
import argparse
import threading

from os import listdir, makedirs
from os.path import isfile, join, getmtime, getctime, exists, abspath

from sys import exit

# Bibliotecas do projeto
from wifiles import WiFiles
from winet import WiNet

parser = argparse.ArgumentParser(description='''Compara diretórios e sincroniza
                                    arquivos.''')
parser.add_argument('-d', '--directory', type=str, required=True,
                    help='''Caminho para o diretório a ser sincronizado
                            (de preferência, use o caminho completo)''')
parser.add_argument('-n', '--hostname', type=str, required=False,
                    help='''Nome de rede do outro computador (caso não
                            especificado, será feita uma busca automática)''')
parser.add_argument('-s', '--server', default=False, const=True, action='store_const',
                    help='''Forçar modo servidor''')

def main(args):
    # Prepara o gerenciador de arquivos
    direc = WiFiles(abspath(args.directory))

    # Prepara o gerenciador de rede
    # O argumento -s força o modo servidor
    if args.server:
        net = WiNet(direc, args.hostname, True)
        net.server()
    else:
        net = WiNet(direc, args.hostname, False)
        net.client()

    # Salva os dados no diretório para a próxima sincronização
    direc.save()

if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
