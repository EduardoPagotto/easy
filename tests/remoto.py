#!/usr/bin/env python3
'''
Created on 20250129
Update on 20250325
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

# params = {'dir': 'dados_db','file':'remoto.json'}
# encoded_params = urllib.parse.urlencode(params)
#final_url = f'{SFTP_DATA}?{encoded_params}'

#SFTP_DATA = 'sftp://uctest:Zaq12wsX@192.168.0.102'
#SFTP_DATA = 'sftp://uctest:Zaq12wsX@192.168.0.102:/data/arquivo.txt'
#SFTP_DATA = 'sftp://uctest:Zaq12wsX@192.168.0.102:/home/uctest/'

#SFTP_DATA = 'sftp://uctest:Zaq12wsX@192.168.0.102:/home/uctest/?dir=dados_db&file=remoto.json'


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('remoto')

def get_env():
    try:
        with open('.env', 'r') as fh:
            vars_dict = dict(
                tuple(line.replace('\n', '').split('='))
                for line in fh.readlines() if not line.startswith('#')
            )

        os.environ.update(vars_dict)
    except Exception as exp:
        logger.critical("Erro Carga de parametros")

if __name__ == "__main__":

    get_env()

    SFTP_DATA = os.environ.get('SFTP')

    path_mng = PathLocalMng(4)

    # Monta SFTP para acesso ao DB
    with SSHFS(SFTP_DATA, False, path_mng) as mnt_remote:

        path_db = mnt_remote.get_path('dados_db')
        #path_db = mnt_remote.get_local()

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
