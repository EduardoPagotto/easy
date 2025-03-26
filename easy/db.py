'''
Created on 20250208
Update on 20250325
@author: Eduardo Pagotto
'''

import os
from typing import Optional
from tinydb.database import TinyDB
from tinydb.storages import Storage
from tinydb.table import Table

from easy.path_mng import PathLocalMng

__all__ = ('JsonDB','JsonDBSSH')

class JsonDB(object):
    def __init__(self, foldername : str, database: str, storage : Storage, cache_size : int = 50):
        """Create/acess a json data file

        Args:
            foldername (str): folder where .json stay
            database (str): nome of json file without .json
            storage (Storage): Class used to deal with filesystem
            cache_size (int, optional):  number of insert or update until automatic flush do file. Defaults to 50.
        """
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
        """Force write pending in json file
        """
        self.tinydb.storage.flush()

    def tables_names(self):
        """List os tables in json file

        Returns:
            list[str]: _description_
        """
        return list(self.tinydb.tables())

class JsonDBSSH(object):
    def __init__(self, sshfs_url : str,  path_mng : Optional[PathLocalMng], storage : Storage, cache_size : int = 1000):
        """Create a temporary conection to access remote json data file

        Args:
            sshfs_url (str): sftp url
            path_mng (Optional[PathLocalMng]): path manager to get a valid free local path to mount
            cache_size

        """

        self.tinydb = TinyDB(
            sshfs_url = sshfs_url,
            path_mng = path_mng,
            storage = storage,
            cache_size = cache_size)

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
        """Force write pending in json file
        """
        self.tinydb.storage.flush()

    def tables_names(self) -> list[str]:
        """List os tables in json file

        Returns:
            list[str]: _description_
        """
        return list(self.tinydb.tables())
