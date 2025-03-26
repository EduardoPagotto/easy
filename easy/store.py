'''
Created on 20250208
Update on 20250325
@author: Eduardo Pagotto
'''

import json
import logging
import os
from datetime import datetime

from typing import Any, Dict, Optional
from tinydb.storages import Storage

from easy.path_mng import PathLocalMng
from easy.sshfs import SSHFS

logger = logging.getLogger(__name__)

__all__ = ('DumpStor', 'DumpStorSSH')

class DumpStor(Storage):
    def __init__(self, filename : str, cache_size : int):
        """Create/acess a json data file

        Args:
            filename (str): path file name of json file
            cache_size (int): number of insert or update until automatic flush do file
        """

        self.filename = filename
        self.cache_size = cache_size
        self.last_read = 0
        self.tot_read = 0
        self.tot_write = 0

        self.cache = None
        self._cache_modified_count = 0

        self.exist_file = True

    def read(self)-> Optional[Dict[str, Dict[str, Any]]]:
        """Read entry used to get data in file

        Returns:
            Optional[Dict[str, Dict[str, Any]]]: dataof json in dictionary
        """

        if self.cache:
            return self.cache

        if self.exist_file:

            try:
                logger.info("json opening %s", self.filename)
                with open(self.filename, 'r') as handle:
                    self.cache =  json.load(handle)

                    if '_SystemDB' in self.cache:
                        self.tot_read += 1
                        self.tot_write = self.cache['_SystemDB']['writes']
                        self.last_read = self.cache['_SystemDB']['reads']
                        self.cache.pop('_SystemDB')

                    return self.cache

            except json.JSONDecodeError:
                logger.error('json %s malformed', self.filename)
            except FileNotFoundError:
                logger.warning('json %s not exist', self.filename)

        self.exist_file = False
        return None

    def write(self, data: Dict[str, Dict[str, Any]]):
        """Write dictionary to file json

        Args:
            data (Dict[str, Dict[str, Any]]): data to save
        """

        self.cache = data
        self._cache_modified_count += 1

        # Check if we need to flush the cache
        if self._cache_modified_count >= self.cache_size:
            self.flush()

    def flush(self):
        """execute a write pendents
        """

        if self._cache_modified_count == 0:
            return

        logger.warning('flush %s with %d transactions.', self.filename, self._cache_modified_count)

        self.tot_write += 1
        self.tot_read += self.last_read
        self.cache['_SystemDB'] = {'reads': self.tot_read, 'writes':self.tot_write,'last_save':datetime.now().isoformat()}

        json_object = json.dumps(self.cache, ensure_ascii=False)

        if os.path.isfile(self.filename):
            os.unlink(self.filename)
        else:
            logger.warning('json %s will be create',self.filename)
            self.exist_file = True

        with open(self.filename, "w") as outfile:
            outfile.write(json_object)
            self._cache_modified_count = 0

    def close(self):
        """automatic flush in close
        """

        self.flush()
        self.tot_read = 0
        self.tot_write = 0
        self.last_read = 0
        self.cache = None
        self.exist_file = False


class DumpStorSSH(Storage):
    def __init__(self,  sshfs_url : str,  path_mng : PathLocalMng, cache_size : int):
        """_sumCreate a temporary conection to access remote json data filemary_

        Args:
            mount_point (str): loacal mount point used to create/use directory structure of json file
            conn (str): directory/file used to json file
            sftp_cfg (dict): dictionary with user/host/pass where json file stay
            cache_size (int): number of insert or update until automatic flush do file.
        """

        self.sshfs_url = sshfs_url
        self.path_mng = path_mng

        self.cache_size = cache_size
        self.last_read = 0
        self.tot_read = 0
        self.tot_write = 0

        self.cache = None
        self._cache_modified_count = 0

        self.exist_file = True

    def read(self)-> Optional[Dict[str, Dict[str, Any]]]:
        """Read entry used to get data in file

        Returns:
            Optional[Dict[str, Dict[str, Any]]]: dataof json in dictionary
        """

        if self.cache:
            return self.cache

        if self.exist_file:

            try:
                path_filename = ''
                with SSHFS(self.sshfs_url, False, self.path_mng) as remote:

                    path_filename = remote.get_path_filename()
                    logger.info("json opening %s", path_filename)
                    with open(path_filename, 'r') as handle:
                        self.cache =  json.load(handle)

                        if '_SystemDB' in self.cache:
                            self.tot_read += 1
                            self.tot_write = self.cache['_SystemDB']['writes']
                            self.last_read = self.cache['_SystemDB']['reads']
                            self.cache.pop('_SystemDB')

                        return self.cache

            except json.JSONDecodeError:
                logger.error('json %s malformed', path_filename)
            except FileNotFoundError:
                logger.warning('json %s not exist', path_filename)

        self.exist_file = False
        return None


    def write(self, data: Dict[str, Dict[str, Any]]):
        """Write dictionary to file json

        Args:
            data (Dict[str, Dict[str, Any]]): data to save
        """

        self.cache = data
        self._cache_modified_count += 1

        # Check if we need to flush the cache
        if self._cache_modified_count >= self.cache_size:
            self.flush()

    def flush(self):
        """execute a write pendents
        """

        if self._cache_modified_count == 0:
            return

        path_filename = ''
        with SSHFS(self.sshfs_url, False, self.path_mng) as remote:

            path_filename = remote.get_path_filename()

            logger.warning('flush %s with %d transactions.', path_filename, self._cache_modified_count)

            self.tot_write += 1
            self.tot_read += self.last_read
            self.cache['_SystemDB'] = {'reads': self.tot_read, 'writes':self.tot_write,'last_save':datetime.now().isoformat()}

            json_object = json.dumps(self.cache, ensure_ascii=False)

            if os.path.isfile(path_filename):
                os.unlink(path_filename)
            else:
                logger.warning('json %s will be create',path_filename)
                self.exist_file = True

            with open(path_filename, "w") as outfile:
                outfile.write(json_object)
                self._cache_modified_count = 0

    def close(self):
        """automatic flush in close
        """

        self.flush()
        self.tot_read = 0
        self.tot_write = 0
        self.last_read = 0
        self.cache = None
        self.exist_file = False
