#!/usr/bin/env python3
'''
Created on 20250129
Update on 20250325
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
from easy.db import JsonDBSSH
from easy.sshparamiko import SSHParamiko

SFTP_DATA = 'sftp://uctest:Zaq12wsX@192.168.0.102:?dir=dados_db&file=paramiko.json'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logging.getLogger('paramiko').setLevel(logging.WARNING)
logger = logging.getLogger('param')

def simples_write_read():

    # Teste escrita json no SFTP
    with SSHParamiko(SFTP_DATA) as remote:

        teste = {'nome': 'locutus', 'idade':5000}
        remote.write_json(teste, 't1.json')

        logger.info('escrita OK')

    # Teste leitura no SFTP
    with SSHParamiko(SFTP_DATA) as remote:

        with remote.sftp.open('t1.json', 'r') as handle:
            handle.prefetch()
            cache =  json.load(handle)
            logger.info(str(cache))

            logger.info('leitura OK')

def teste_db():

    with JsonDBSSH(sshfs_url=SFTP_DATA, path_mng=None, storage=DumpStorParamiko, cache_size=100) as db_remote:

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
