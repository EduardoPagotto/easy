#!/usr/bin/env python3
'''
Created on 20250129
Update on 20250305
@author: Eduardo Pagotto
'''

import json
import logging
from datetime import datetime

from tinydb import where
from tinydb.table import Table

import sys
sys.path.append('.')

from easy.store_para import DumpStorParamiko
from easy.db import JsonLazzyDB
from easy.sshparamiko import SSHParamiko

# Dados de conexao do host
SFTP_DATA = {"host": "192.168.0.102",
             "user": "uctest",
             "passwd": "Zaq12wsX",
             "remote": ".",
             "local": "/mnt/remote_db"}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')


logging.getLogger('paramiko').setLevel(logging.WARNING)
logger = logging.getLogger('param')

def simples_write_read():

    # Teste escrita json no SFTP
    with SSHParamiko(SFTP_DATA) as remote:

        aa = remote.get_path('teste_z1')
        teste = {'nome': 'locutus', 'idade':5000}
        remote.write_json(teste, 't1.json')

        logger.info('escrita OK')

    # Teste leitura no SFTP
    with SSHParamiko(SFTP_DATA) as remote:
        aa = remote.get_path('teste_z1')
        with remote.sftp.open('t1.json', 'r') as handle:
            handle.prefetch()
            cache =  json.load(handle)
            logger.info(str(cache))

            logger.info('leitura OK')

def teste_db():

    with JsonLazzyDB('', 'dados_db/param', SFTP_DATA, storage=DumpStorParamiko, cache_size=100) as db_remote:

        tbl : Table = db_remote.Tabela

        id : int = 0
        rec = tbl.get(where('_id')=='info' )
        if not rec:
            rec = {'_id':'info',
                'nome' : 'John',
                'idade': 55,
                'last': datetime.now().isoformat()}

            id = tbl.insert(rec)
        else:
            id = rec.doc_id

        tbl.insert({'_id':'teste',
                    'nome' : 'John',
                    'idade': 55,
                    'last': datetime.now().isoformat()})

        logger.info('Result doc_id: %d val:%s', id, str(rec))

if __name__ == "__main__":

    logger.info('inicio')
    try:
        # simples_write_read()
        teste_db()

    except Exception as exp:
        logger.critical(str(exp.args))
