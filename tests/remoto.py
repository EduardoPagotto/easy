#!/usr/bin/env python3
'''
Created on 20250129
Update on 20250326
@author: Eduardo Pagotto
'''

import logging
from datetime import datetime

import os
import sys

sys.path.append('.')

from easy.db import JsonDB
from easy.path_mng import PathLocalMng
from easy.sshfs import SSHFS
from easy.store import DumpStor

from tinydb import where
from tinydb.table import Table

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('remoto')

if __name__ == "__main__":

    SFTP_DATA = 'sftp://uctest:Zaq12wsX@192.168.1.214'

    path_mng = PathLocalMng(4)

    # Monta SFTP para acesso ao DB
    with SSHFS(SFTP_DATA, False, path_mng) as mnt_remote:

        path_db = mnt_remote.get_path('dados_db')

        with JsonDB(path_db, 'remoto', storage=DumpStor) as db_remote:

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
