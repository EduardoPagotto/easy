#!/usr/bin/env python3
'''
Created on 20250129
Update on 20250129
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
SFTP_DATA = {'host': '127.0.0.1',
             'user': 'remote01',
             'passwd': 'ZZZZZ',
             'remote': '.',
             'local': '/mnt/shared'}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('basic')

if __name__ == "__main__":

    # Monta SFTP para acesso ao DB
    logger.info('Conecta ao sftp')
    with SSHFS(SFTP_DATA, False) as mnt_remote:

        logger.info('Pega o path')
        path_db = mnt_remote.get_path('dados_db')

        logger.info('Cria arquivo json banco01.json')
        with JsonDB(path_db, 'banco01', storage=DumpStor) as db_remote:

            logger.info("Cria ou oega tabela se ja existir")
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
