#!/usr/bin/env python3
'''
Created on 20250129
Update on 20250302
@author: Eduardo Pagotto
'''

import logging
from datetime import datetime

from tinydb import where
from tinydb.table import Table

import sys
sys.path.append('.')

from easy import JsonLazzyDB, DumpStorSSH

# Dados de conexao do host
SFTP_DATA = {"host": "192.168.0.102",
             "user": "uctest",
             "passwd": "Zaq12wsX",
             "remote": ".",
             "local": "/mnt/remote_db"}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('lazzy')

if __name__ == "__main__":

    with JsonLazzyDB('dados_db', 'banco01', SFTP_DATA, storage=DumpStorSSH, cache_size=100) as db_remote:

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
