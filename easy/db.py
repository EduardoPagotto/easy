'''
Created on 20250208
Update on 20250305
@author: Eduardo Pagotto
'''

import os
from tinydb.database import TinyDB
from tinydb.storages import Storage
from tinydb.table import Table

__all__ = ('JsonDB','JsonLazzyDB')

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

class JsonLazzyDB(object):
    def __init__(self, mount_point : str,  conn : str, sftp_cfg : dict, storage : Storage, cache_size : int = 1000):
        """Create a temporary conection to access remote json data file

        Args:
            mount_point (str): loacal mount point used to create/use directory structure of json file
            conn (str): directory/file used to json file
            sftp_cfg (dict): dictionary with user/host/pass where json file stay
            storage (Storage): Class used to deal with ssh/paraminko
            cache_size (int, optional): number of insert or update until automatic flush do file. Defaults to 1000.
            <p>
            <b>Exmaple:</b>
            JsonLazzyDB('/mnt/remote/', 'databases/data' val['sftp], DumpStorSSH, 5000)<p>
            <i>json file stay in: '/mnt/remote/databases/data.json'</i>
        """

        self.tinydb = TinyDB(
            conn = conn,
            sftp_cfg = sftp_cfg,
            storage = storage,
            mount_point = mount_point,
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

    def tables_names(self) -> list[str]:
        """List os tables in json file

        Returns:
            list[str]: _description_
        """
        return list(self.tinydb.tables())
