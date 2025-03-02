'''
Created on 20250208
Update on 20250302
@author: Eduardo Pagotto
'''

import os
from tinydb.database import TinyDB
from tinydb.storages import Storage
from tinydb.table import Table

__all__ = ('JsonDB','JsonLazzyDB')

class JsonDB(object):
    def __init__(self, foldername : str, database: str, storage : Storage, cache_size : int = 50):
        try:
            os.mkdir(foldername)
        except OSError as x:
            pass

        self.tinydb = TinyDB(
            os.path.join(foldername, database + u".json"),
            storage=storage,
            cache_size = cache_size
        )

    def __enter__(self):
        """Use the database as a context manager."""
        return self

    def __exit__(self, *args):
        """Close the storage instance when leaving a context."""
        self.tinydb.close()

    def __getattr__(self, name : str) -> Table:
        """Gets a new or existing table"""
        return self.tinydb.table(name=name)

    def __getitem__(self, name : str) -> Table:
        """Gets a new or existing table"""
        return self.tinydb.table(name=name)

    def flush(self):
        self.tinydb.storage.flush()

    def tables_names(self):
        return list(self.tinydb.tables())

class JsonLazzyDB(object):
    def __init__(self, conn : str, sftp_cfg : dict, storage : Storage, cache_size : int = 1000):

        self.tinydb = TinyDB(
            conn = conn,
            sftp_cfg = sftp_cfg,
            storage = storage,
            cache_size = cache_size
        )

    def __enter__(self):
        """Use the database as a context manager."""
        return self

    def __exit__(self, *args):
        """Close the storage instance when leaving a context."""
        self.tinydb.close()

    def __getattr__(self, name : str) -> Table:
        """Gets a new or existing table"""
        return self.tinydb.table(name=name)

    def __getitem__(self, name : str) -> Table:
        """Gets a new or existing table"""
        return self.tinydb.table(name=name)

    def flush(self):
        self.tinydb.storage.flush()

    def tables_names(self):
        return list(self.tinydb.tables())
