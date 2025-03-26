#!/usr/bin/env python3
'''
Created on 20250129
Update on 20250325
@author: Eduardo Pagotto
'''

import logging
from datetime import datetime

import sys
sys.path.append('.')

from tinydb import where
from tinydb.table import Table

from easy.path_mng import PathLocalMng
from easy import JsonDBSSH, DumpStorSSH

# Dados de conexao do host
SFTP_DATA = 'sftp://uctest:Zaq12wsX@192.168.0.102:?dir=dados_db&file=lazze.json'

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('lazzy')

if __name__ == "__main__":

    path_mng = PathLocalMng(4)

    with JsonDBSSH(SFTP_DATA,  path_mng, storage=DumpStorSSH, cache_size=100) as db_remote:

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
