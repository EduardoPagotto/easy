'''
Created on 20250208
Update on 20250210
@author: Eduardo Pagotto
'''

import logging
import os
from tinydb.database import TinyDB
from tinydb.storages import Storage
from tinydb.table import Table

logger = logging.getLogger(__name__)

class EasyAcc(object):
    def __init__(self, foldername : str, database: str, storage : Storage):
        self._foldername = foldername
        try:
            os.mkdir(foldername)
        except OSError as x:
            pass

        logger.info("DB open: %s", database)

        self.tinydb = TinyDB(
            os.path.join(foldername, database + u".json"),
            storage=storage
        )

    def __enter__(self):
        """Use the database as a context manager."""
        return self

    def __exit__(self, *args):
        """Close the storage instance when leaving a context."""
        self.close()

    def table(self, name : str) -> Table:
         """Gets a new or existing table"""
         return self.tinydb.table(name=name)

    # def __getattr__(self, name):
    #     """Gets a new or existing collection"""
    #     return self.tinydb.table(name=name)

    # def __getitem__(self, name):
    #     """Gets a new or existing collection"""
    #     return self.tinydb.table(name=name)

    def close(self):
        #logger.info("DB close: %s", database)
        self.tinydb.close()

    def flush(self):
        self.tinydb.storage.flush()

    def tables_names(self):
        return list(self.tinydb.tables())
