'''
Created on 20250208
Update on 20250301
@author: Eduardo Pagotto
'''

import logging
import os
from tinydb.database import TinyDB
from tinydb.storages import Storage
from tinydb.table import Table

from easy.sshfs import SSHFS

logger = logging.getLogger(__name__)

__all__ = ('JsonDB','JsonLazzyDB')

class JsonDB(object):
    def __init__(self, foldername : str, database: str, storage : Storage, cache_size : int = 50):
        try:
            os.mkdir(foldername)
        except OSError as x:
            pass

        logger.info("DB open: %s", database)

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
        self.close()

    def __getattr__(self, name : str) -> Table:
        """Gets a new or existing table"""
        return self.tinydb.table(name=name)

    def __getitem__(self, name : str) -> Table:
        """Gets a new or existing table"""
        return self.tinydb.table(name=name)

    def close(self):
        self.tinydb.close()

    def flush(self):
        self.tinydb.storage.flush()

    def tables_names(self):
        return list(self.tinydb.tables())

class JsonLazzyDB(object):
    def __init__(self, foldername : str, database: str, sftp_cfg : dict, storage : Storage, cache_size : int = 1000):

        with SSHFS(sftp_cfg, False) as remote:

            path_remoto : str = remote.get_path(foldername)
            file : str = os.path.join(path_remoto, database + u".json")

            logger.info("json open: %s", file)

            self.tinydb = TinyDB(
                filename = file,
                sftp_cfg = sftp_cfg,
                storage = storage,
                cache_size = cache_size
            )

    def __enter__(self):
        """Use the database as a context manager."""
        return self

    def __exit__(self, *args):
        """Close the storage instance when leaving a context."""
        self.close()

    def __getattr__(self, name : str) -> Table:
        """Gets a new or existing table"""
        return self.tinydb.table(name=name)

    def __getitem__(self, name : str) -> Table:
        """Gets a new or existing table"""
        return self.tinydb.table(name=name)

    def close(self):
        self.tinydb.close()

    def flush(self):
        self.tinydb.storage.flush()

    def tables_names(self):
        return list(self.tinydb.tables())
