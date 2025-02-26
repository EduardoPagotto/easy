#!/usr/bin/env python3
'''
Created on 20250129
Update on 20250129
@author: Eduardo Pagotto
'''

import logging
from datetime import datetime
from pathlib import Path

from tinydb import where
from tinydb.table import Table

import sys
sys.path.append('.')

from easy import JsonDB, DumpStor

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('basic')

if __name__ == "__main__":

    # path do arquivo
    path_db = './data'
    Path(path_db).mkdir(parents=True, exist_ok=True)

    # Cria arquivo json banco01.json
    with JsonDB(path_db, 'banco01', storage=DumpStor) as db_remote:

        # Cria ou referencia tabela se ja existir
        tbl : Table = db_remote.table('tabela')

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
