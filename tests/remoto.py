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

from easy import SSHFS, JsonDB, DumpStor

# Dados de conexao do host
SFTP_DATA = {"host": "192.168.0.102",
             "user": "uctest",
             "passwd": "Zaq12wsX",
             "remote": ".",
             "local": "/mnt/remote_db"}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('remoto')

if __name__ == "__main__":

    # Monta SFTP para acesso ao DB
    with SSHFS(SFTP_DATA, False) as mnt_remote:

        path_db = mnt_remote.get_path('dados_db')

        with JsonDB(path_db, 'banco01', storage=DumpStor) as db_remote:

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

            logger.info('Result doc_id: %d val:%s', id, str(rec))
