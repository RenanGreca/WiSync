#!/usr/bin/env python
# coding=utf-8

# WiSync.py
# Copyright (C) 2015 Renan Greca <rdmg11@inf.ufpr.com>

# Bibliotecas auxiliares
import argparse

from os import listdir, makedirs
from os.path import isfile, join, getmtime, getctime, exists

from sys import exit

# Bibliotecas do projeto
from wifiles import Dir
from winet import Net

parser = argparse.ArgumentParser(description='''Compara diretórios e sincroniza
                                    arquivos.''')
parser.add_argument('-d', '--directory', type=str, required=True,
                    help='''Caminho para o diretório a ser sincronizado
                         	(de preferência, use o caminho completo)''')
parser.add_argument('-n', '--hostname', type=str, required=False,
                    help='''Nome de rede do outro computador (caso não
                    		especificado, será feita uma busca automática)''')

def main(args):
	#dir = Dir(args.directory)
	#dir.save()

	net = Net()
	net.client()

if __name__ == '__main__':
	args = parser.parse_args()
	main(args)
